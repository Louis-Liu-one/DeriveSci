'''MathProbsOnline.PythonAnyWhere.com
Copyright (c) 2026 Louis Liu  All rights reserved.

数据库模型模块，实现网站所需的数据库操作。
'''

import io
import csv
import json
import datetime
import functools
import mimetypes

from flask import url_for
from flask_login import LoginManager, UserMixin, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import MetaData

from anschecker import check_answers, testpoints_passedlist


__all__ = [
    'init_app', 'db', 'csv2list', 'list2csv', 'utcfromnow',
    'find_user', 'register_user', 'unregister_user',
    'Prob', 'ProbImage', 'ProbLabel', 'get_prob', 'search_probs', 'add_prob',
    'get_solution', 'add_solution', 'add_images', 'add2labels',
    'Comment', 'get_comment', 'clear_comments', 'update_chatlastvisit',
]

convention = {
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s',
}
metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)
login_manager = LoginManager()
login_manager.login_view = 'login'
migrate = Migrate(db=db)


def init_app(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
    db.init_app(app)
    migrate.init_app(app)
    login_manager.init_app(app)


def csv2list(csvstr):
    return next(csv.reader((csvstr,), skipinitialspace=True))


def list2csv(ls):
    csvstr = io.StringIO()
    writer = csv.writer(csvstr)
    writer.writerow(list(ls))
    return csvstr.getvalue().splitlines()[0]


_utcnow = functools.partial(datetime.datetime.now, datetime.UTC)


def utcfromnow(timestamp):
    return _utcnow() - timestamp.astimezone(datetime.UTC)


# =========================== 用户数据库与登录系统 ===========================


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    columns = 'uid', 'name', 'password'
    uid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    gender = db.Column(db.Integer, default=0)
    password = db.Column(db.String(256), nullable=False)
    introduction = db.Column(db.Text)
    avatar = db.Column(db.LargeBinary)
    avmimetype = db.Column(db.String(64))
    avlastmodified = db.Column(db.DateTime, default=_utcnow, onupdate=_utcnow)
    submissions = db.relationship(
        'Submission', backref='user', cascade='all, delete')
    uploadedprobs = db.relationship('Prob', backref='source')
    solutions = db.relationship('ProbSolution', backref='user')
    comments = db.relationship('Comment', backref='user')
    cmtlastvisit = db.Column(db.DateTime, default=_utcnow)
    isadmin = db.Column(db.Boolean, default=False)

    def verify_password(self, password):
        return False if self.password is None else \
            check_password_hash(self.password, password)

    def edit_profile(
            self, name, password, password_confirmation, avatarfile, gender):
        user_exists = db.session.query(
            User.query.filter_by(name=name).exists()).scalar()
        if name != self.name and user_exists:
            return '用户名与其他用户重复。'
        elif password != password_confirmation:
            return '密码与确认密码不一致。'
        elif not name:
            return '用户名不能为空。'
        avatardata = avatarfile.read()
        if name and name != self.name:
            self.name = name
        if password and not self.verify_password(password):
            self.password = generate_password_hash(password)
        if avatardata:
            self.avatar = avatardata
            self.avmimetype = mimetypes.guess_type(avatarfile.filename)[0]
            self.avlastmodified = _utcnow()
        if gender != self.gender:
            self.gender = gender
        db.session.commit()

    def get_probscores(self):
        probscores = {}
        for submission in self.submissions:
            prob = submission.prob
            if prob not in probscores or prob in probscores \
                    and probscores[prob] < submission.score:
                probscores[prob] = submission.score
        return probscores

    def get_passedprobs(self):
        return sorted([
            prob for prob, score in self.get_probscores().items()
            if score == 100])

    def unread_reply_comments(self):
        is_mine = Comment.replyto.has(Comment.uid == self.uid)
        return Comment.query.filter(
            is_mine if self.cmtlastvisit is None
            else is_mine & (self.cmtlastvisit < Comment.timestamp)).order_by(
            Comment.timestamp.desc()).all()

    def unread_comments_on_my_probs(self):
        probnos = [prob.probno for prob in self.uploadedprobs]
        if not probnos:
            return []
        query = Comment.query.filter(
            Comment.post_type == 0, Comment.post_ident.in_(probnos),
            Comment.replyto_id.is_(None))
        if self.cmtlastvisit is not None:
            query = query.filter(Comment.timestamp > self.cmtlastvisit)
        return query.order_by(Comment.timestamp.desc()).all()

    def unread_comments_on_my_solutions(self):
        sol_ids = [solution.get_post_ident() for solution in self.solutions]
        if not sol_ids:
            return []
        query = Comment.query.filter(
            Comment.post_type == 1, Comment.post_ident.in_(sol_ids),
            Comment.replyto_id.is_(None))
        if self.cmtlastvisit is not None:
            query = query.filter(Comment.timestamp > self.cmtlastvisit)
        return query.order_by(Comment.timestamp.desc()).all()

    def unread_comments_count(self):
        reply_query = Comment.query.filter(
            Comment.replyto.has(Comment.uid == self.uid))
        probnos = [prob.probno for prob in self.uploadedprobs]
        solution_ids = [
            solution.get_post_ident() for solution in self.solutions]
        prob_query = Comment.query.filter(
            Comment.post_type == 0, Comment.post_ident.in_(probnos),
            Comment.replyto_id.is_(None)) if probnos else None
        sol_query = Comment.query.filter(
            Comment.post_type == 1, Comment.post_ident.in_(solution_ids),
            Comment.replyto_id.is_(None)) if solution_ids else None
        if self.cmtlastvisit is not None:
            reply_query = reply_query.filter(
                Comment.timestamp > self.cmtlastvisit)
            if prob_query is not None:
                prob_query = prob_query.filter(
                    Comment.timestamp > self.cmtlastvisit)
            if sol_query is not None:
                sol_query = sol_query.filter(
                    Comment.timestamp > self.cmtlastvisit)
        total = reply_query.count()
        if prob_query is not None:
            total += prob_query.count()
        if sol_query is not None:
            total += sol_query.count()
        return total

    def unread_comment_sections(self):
        return {
            'replies': self.unread_reply_comments(),
            'prob_comments': self.unread_comments_on_my_probs(),
            'solution_comments': self.unread_comments_on_my_solutions(),
        }

    def update_cmtlastvisit(self):
        self.cmtlastvisit = _utcnow()
        db.session.commit()

    def chat_to(self, uid, msg):
        message = Comment(
            user=self, content=str(msg), post_type=2, post_ident=str(uid))
        db.session.add(message)
        db.session.commit()

    def all_chats(self, from_time=None):
        if from_time is None:
            from_time = datetime.datetime.min
        chats_list = Comment.query.filter(
            Comment.post_type == 2, Comment.timestamp > from_time,
            (Comment.uid == self.uid) | (Comment.post_ident == str(self.uid))
            ).order_by(Comment.timestamp.asc()).all()
        chats, lastvisits = {}, {}
        for chatmsg in chats_list:
            other, othersend = chatmsg.uid, True
            if other == self.uid:
                other, othersend = int(chatmsg.post_ident), False
            if other not in chats:
                chats[other] = {'unread': 0, 'messages': []}
            chats[other]['messages'].append({
                'content': chatmsg.content, 'othersend': othersend,
                'timestamp': chatmsg.timestamp.isoformat()})
            if other not in lastvisits:
                lastvisits[other] = max(get_chatlastvisit(
                    self.uid, other).lastvisit, from_time)
            chats[other]['unread'] += othersend \
                and lastvisits[other] < chatmsg.timestamp
        return chats

    def unread_chats_num(self):
        chats_list = Comment.query.filter(
            Comment.post_type == 2, Comment.post_ident == str(self.uid)
            ).order_by(Comment.timestamp.asc()).all()
        unread_num, lastvisits = 0, {}
        for chatmsg in chats_list:
            other = chatmsg.uid
            if other not in lastvisits:
                lastvisits[other] = get_chatlastvisit(
                    self.uid, other).lastvisit
            unread_num += lastvisits[other] < chatmsg.timestamp
        return unread_num

    def url(self, anchor=None, **kwargs):
        return url_for('users', uid=self.uid, _anchor=anchor, **kwargs)

    def get_id(self):
        return self.uid


def find_user(val, key='uid'):
    if not val or key not in User.columns:
        return None
    user = db.session.get(User, val) if key == 'uid' \
        else User.query.filter_by(**{key: val}).first()
    return user


@login_manager.user_loader
def load_user(uid):
    return find_user(uid)


def register_user(name, gender, password, password_confirmation, avatarfile):
    user_exists = db.session.query(
        User.query.filter_by(name=name).exists()).scalar()
    if name and password and not user_exists \
            and password == password_confirmation:
        user = User(
            name=name, gender=gender,
            password=generate_password_hash(password))
        if avatarfile is not None:
            user.avatar = avatarfile.read()
            user.avmimetype = mimetypes.guess_type(avatarfile.filename)[0]
        db.session.add(user)
        db.session.commit()
        return True, user
    elif password != password_confirmation:
        return False, '密码与确认密码不一致。'
    elif user_exists:
        return False, '用户名与其他用户重复。'
    else:
        return False, '账户创建失败。'


def unregister_user(user):
    if user is not None:
        db.session.delete(user)
        db.session.commit()


# =========================== 题目与图片数据库 ===========================


prob_label = db.Table(
    'probs_labels', db.Column(
        'probno', db.String(16),
        db.ForeignKey('probs.probno'), primary_key=True),
    db.Column(
        'labelname', db.String(16),
        db.ForeignKey('labels.labelname'), primary_key=True))


class Prob(db.Model):
    __tablename__ = 'probs'
    probno = db.Column(db.String(16), primary_key=True)
    probtitle = db.Column(db.String(64))
    problabels = db.relationship(
        'ProbLabel', secondary=prob_label, back_populates='probs',
        collection_class=set)
    statement = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text)
    solutions = db.relationship(
        'ProbSolution', backref='prob', cascade='all, delete')
    sourceuid = db.Column(db.Integer, db.ForeignKey('users.uid'))
    submissions = db.relationship(
        'Submission', backref='prob', cascade='all, delete')
    images = db.relationship(
        'ProbImage', backref='prob', cascade='all, delete')
    review_status = db.Column(db.Integer, default=-1)
    isofficial = db.Column(db.Boolean, default=False)
    review_comment = db.Column(db.Text)

    def get_answer(self):
        if not self.answer:
            return []
        answer = json.loads(self.answer)
        if not isinstance(answer, list):
            return []
        return answer

    def check_answers(self, userans):
        answers = self.get_answer()
        if not answers:
            return None, []
        if isinstance(userans, str):
            userans_list = [userans]
        elif isinstance(userans, list):
            userans_list = userans
        else:
            userans_list = [str(userans)]

        answer_evals = []
        testpoints_list = []
        for i, sub in enumerate(answers):
            ua = userans_list[i] if i < len(userans_list) else ''
            ua_eval, tps = check_answers(sub, ua)
            answer_evals.append(ua_eval)
            testpoints_list.append(tps)
        return answer_evals, testpoints_list

    def add_submission(self, user, answer):
        answer_eval, testpoints = self.check_answers(answer)
        passedlist = []
        for sub in testpoints:
            passedlist.extend(testpoints_passedlist(sub))
        submission = Submission(
            user=user, answer=json.dumps(answer)
            if not isinstance(answer, str) else answer,
            ispassed=all(passedlist) if passedlist else False,
            score=100 * sum(passedlist) // len(passedlist)
            if passedlist else 0)
        db.session.add(submission)
        submission.prob = self
        db.session.commit()
        return answer_eval, testpoints, submission

    def get_toplevel_comments(self):
        return Comment.query.filter(
            Comment.post_type == 0, Comment.post_ident == self.probno,
            Comment.replyto_id.is_(None)).order_by(
            Comment.timestamp.desc()).all()

    def edit(self, probtitle, problabels, statement, answer):
        if probtitle:
            self.probtitle = probtitle
        if statement:
            self.statement = statement
        self.answer = answer
        self.problabels = {get_label(
            labelname, create=True) for labelname in problabels}
        db.session.commit()

    def viewable_for(self, user):
        return self.review_status == 1 or user.is_authenticated and (
            user == self.source or user.isadmin)

    def editable_for(self, user):
        return user.is_authenticated and (user == self.source or user.isadmin)

    def as_labelnames(self):
        return {label.labelname for label in self.problabels}

    def url(self, anchor=None, **kwargs):
        return url_for('probs', probno=self.probno, _anchor=anchor, **kwargs)

    def __str__(self):
        return f'问题 {self.probno}'

    def __lt__(self, prob):
        return self.probno < prob.probno


class Submission(db.Model):
    __tablename__ = 'submissions'
    submitid = db.Column(db.Integer, primary_key=True)
    probno = db.Column(
        db.String(16), db.ForeignKey('probs.probno'), nullable=False)
    userid = db.Column(db.Integer, db.ForeignKey('users.uid'))
    answer = db.Column(db.Text, nullable=False)
    ispassed = db.Column(db.Boolean)
    score = db.Column(db.Integer)

    def __lt__(self, sub):
        return self.probno < sub.probno


class ProbSolution(db.Model):
    __tablename__ = 'solutions'
    probno = db.Column(
        db.String(16), db.ForeignKey('probs.probno'), primary_key=True)
    solno = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.uid'))
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=False)

    def url(self, anchor=None, **kwargs):
        return url_for('solutions', probno=self.probno, solno=self.solno,
                       _anchor=anchor, **kwargs)

    def get_post_ident(self):
        return list2csv([self.probno, self.solno])

    def get_toplevel_comments(self):
        post_ident = self.get_post_ident()
        return Comment.query.filter(
            Comment.post_type == 1, Comment.post_ident == post_ident,
            Comment.replyto_id.is_(None)).order_by(
            Comment.timestamp.desc()).all()

    def edit(self, title, content):
        if title:
            self.title = title
        if content:
            self.content = content
        db.session.commit()

    def viewable_for(self, user):
        return self.prob.viewable_for(user) or user == self.user

    def editable_for(self, user):
        return user.is_authenticated and (user == self.user or user.isadmin)

    def __str__(self):
        return f'问题 {self.probno} 的题解：{self.title}'

    def __lt__(self, solution):
        return self.probno < solution.probno


class ProbImage(db.Model):
    __tablename__ = 'images'
    probno = db.Column(
        db.String(16), db.ForeignKey('probs.probno'), primary_key=True)
    name = db.Column(db.String(64), primary_key=True)
    uid = db.Column(db.Integer)
    size = db.Column(db.Integer)
    mimetype = db.Column(db.String(64))
    data = db.Column(db.LargeBinary)


class ProbLabel(db.Model):
    __tablename__ = 'labels'
    labelname = db.Column(db.String(16), primary_key=True)
    probs = db.relationship(
        'Prob', secondary=prob_label, back_populates='problabels',
        collection_class=set)

    def url(self):
        return url_for('problistoflabel', labelname=self.labelname)


def get_prob(probno):
    return db.session.get(Prob, str(probno))


def search_probs(form, extra_req=None, reviewmode=False):
    requirements = []
    if form.get('probno'):
        requirements.append(Prob.probno == form['probno'])
    if form.get('probtitle'):
        requirements.append(Prob.probtitle.like(f'%{form['probtitle']}%'))
    if form.get('statement'):
        requirements.append(Prob.statement.like(f'%{form['statement']}%'))
    if form.get('problabels'):
        requirements.append(db.or_(Prob.problabels.any(
            ProbLabel.labelname == problabel) for problabel
            in csv2list(form['problabels'])))
    if form.get('source'):
        source = []
        for name in csv2list(form['source']):
            user = find_user(name, 'name')
            if user:
                source.append(user)
        if source:
            requirements.append(db.or_(
                Prob.source == user for user in source))
    if form.get('probtype') in ('officialprobs', 'noofficialprobs'):
        requirements.append(Prob.isofficial == (
            form['probtype'] == 'officialprobs'))
    if reviewmode and form.get('review_status') in (
            'toreview', 'accepted', 'rejected'):
        requirements.append(Prob.review_status == {
            'toreview': -1, 'rejected': 0, 'accepted': 1}
            [form['review_status']])
    flag = bool(requirements)
    if extra_req is not None:
        requirements.append(extra_req)
    if not reviewmode:
        requirements.append(Prob.review_status == 1)
    if not requirements:
        return Prob.query.order_by(Prob.probno.asc()), flag
    return Prob.query.filter(*requirements).order_by(
        Prob.probno.asc()), flag


def add_prob(**kwargs):
    probno = kwargs.get('probno')
    probtitle = kwargs.get('probtitle')
    statement = kwargs.get('statement')
    if not probtitle:
        return False, '题目标题不能为空。'
    elif not statement:
        return False, '题目描述不能为空。'
    elif get_prob(probno) is not None:
        return False, f'以{probno}为编号的题目已存在。'
    prob = Prob(**kwargs)
    db.session.add(prob)
    db.session.commit()
    return True, prob


def get_solution(probno, solno):
    return db.session.get(ProbSolution, (str(probno), int(solno)))


def add_solution(probno, title, content):
    if not title:
        return False, '题解标题不能为空。'
    elif not content:
        return False, '题解内容不能为空。'
    prob = get_prob(probno)
    if not prob:
        return False, '未能找到题目。'
    solution = ProbSolution(
        prob=prob, solno=len(prob.solutions),
        user=current_user, title=title, content=content)
    db.session.add(solution)
    db.session.commit()
    return True, solution


def add_images(probno, imgfiles):
    for imgfile in imgfiles:
        if db.session.get(ProbImage, (probno, imgfile.filename)) is not None:
            return '文件名与已有文件重复。'
    for imgfile in imgfiles:
        imgdata = imgfile.read()
        if len(imgdata):
            img = ProbImage(
                probno=probno, name=imgfile.filename, uid=current_user.uid,
                size=len(imgdata), data=imgdata,
                mimetype=mimetypes.guess_type(imgfile.filename)[0])
            db.session.add(img)
    db.session.commit()


def get_label(labelname, create=False):
    label = db.session.get(ProbLabel, str(labelname))
    if create and label is None:
        label = ProbLabel(labelname=str(labelname))
        db.session.add(label)
        db.session.commit()
    return label


def add2labels(labelnames, prob):
    for labelname in set(labelnames):
        label = get_label(labelname, create=True)
        label.probs.add(prob)
    db.session.commit()


# =========================== 讨论区与私信数据库支持 ===========================


user_chat = db.Table(
    'user_chats', db.Column(
        'uid_receiver', db.Integer, db.ForeignKey(
            'users.uid', ondelete='cascade'), primary_key=True),
    db.Column(
        'uid_sender', db.Integer, db.ForeignKey(
            'users.uid', ondelete='cascade'), primary_key=True),
    db.Column(
        'lastvisit', db.DateTime, nullable=False,
        default=datetime.datetime.min.replace(tzinfo=datetime.UTC)))


def get_chatlastvisit(uid_receiver, uid_sender):
    result = db.session.execute(user_chat.select().where(
        user_chat.c.uid_receiver == uid_receiver,
        user_chat.c.uid_sender == uid_sender)).first()
    if result is None:
        db.session.execute(user_chat.insert().values(
            uid_receiver=uid_receiver, uid_sender=uid_sender))
        result = db.session.execute(user_chat.select().where(
            user_chat.c.uid_receiver == uid_receiver,
            user_chat.c.uid_sender == uid_sender)).first()
        db.session.commit()
    return result


def update_chatlastvisit(uid_receiver, uid_sender):
    exists = get_chatlastvisit(uid_receiver, uid_sender)
    if not exists:
        db.session.execute(user_chat.insert().values(
            uid_receiver=uid_receiver, uid_sender=uid_sender,
            lastvisit=_utcnow()))
    else:
        db.session.execute(user_chat.update().where(
            user_chat.c.uid_receiver == uid_receiver,
            user_chat.c.uid_sender == uid_sender).values(lastvisit=_utcnow()))
    db.session.commit()


class Comment(db.Model):
    __tablename__ = 'comments'
    cmtid = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('users.uid'))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=_utcnow)
    replyto_id = db.Column(db.Integer, db.ForeignKey('comments.cmtid'))
    # 帖子类型为0，帖子为题目，标识符为题目编号
    # 帖子类型为1，帖子为题解，标识符为CSV格式的题目编号与题解编号的组合
    # 帖子类型为2，帖子为私信，标识符为信息接收用户ID，不使用replyto、replies字段
    post_type = db.Column(db.Integer, nullable=False)  # 帖子类型
    post_ident = db.Column(db.Text, nullable=False)    # 帖子标识符
    replyto = db.relationship(
        'Comment', back_populates='replies', remote_side=[cmtid])
    replies = db.relationship(
        'Comment', back_populates='replyto', cascade='all, delete')

    def get_all_replies(self):
        return sorted(sum(
            [comment.get_all_replies() for comment in self.replies],
            start=self.replies.copy()))

    def get_post(self):
        if self.post_type == 0:
            return get_prob(self.post_ident)
        elif self.post_type == 1:
            probno, solno = csv2list(self.post_ident)
            return get_solution(probno, int(solno))
        elif self.post_type == 2:
            return None  # 私信信息，无实际对象
        return None  # 未知帖子类型

    def editable_for(self, user):
        return user.is_authenticated and (user == self.user or user.isadmin)

    def __lt__(self, comment):
        return self.timestamp < comment.timestamp


def get_comment(commentid):
    return db.session.get(Comment, int(commentid))


def clear_comments(post):
    for comment in post.get_toplevel_comments():
        db.session.delete(comment)
    db.session.commit()
