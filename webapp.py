'''MathProbsOnline
Copyright (c) 2026 Louis Liu  All rights reserved.

用户操作：
/login             登录
/logout            登出
/register          注册
/unregister        注销
/edit-profile      编辑信息
/edit-introduction 编辑简介
/users/<uid>       查看他人主页
/post-comment/<post_type>/<post_ident>         发表评论
/post-comment/<post_type>/<post_ident>/<cmtid> 回复评论
/delete-comment                                删除评论
/unread-comments                               未读评论

题目：
/upload-prob         上传题目
/labels/             所有标签
/labels/<labelname>  单个标签
/probs/              题集
/probs/<probno>                 题目<probno>
/probs/<probno>/submit          提交题目<probno>的答案
/probs/<probno>/edit            编辑题目
/probs/<probno>/delete          删除题目
/probs/<probno>/upload-solution 上传题解
/probs/<probno>/solutions/<solno>        查看题解
/probs/<probno>/solutions/<solno>/edit   编辑题解
/probs/<probno>/solutions/<solno>/delete 删除题解

计划部署至：MathProbsOnline.PythonAnyWhere.com
'''

import io
import os
import csv
import json
import random
import hashlib
import datetime
import functools
import mimetypes

from flask import Flask, Response, request, url_for
from flask import render_template, redirect, send_file, make_response
from flask_login import LoginManager, UserMixin, current_user
from flask_login import login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import MetaData

from anschecker import TPStatus, check_answers, testpoints_passedlist, latex


app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
convention = {
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s',
}
metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db, render_as_batch=True)
moment = Moment(app)


def csv2list(csvstr):
    return next(csv.reader((csvstr,), skipinitialspace=True))


def list2csv(ls):
    csvstr = io.StringIO()
    writer = csv.writer(csvstr)
    writer.writerow(list(ls))
    return csvstr.getvalue().splitlines()[0]


_utcnow = functools.partial(datetime.datetime.now, datetime.UTC)


def _utcfromnow(timestamp):
    return _utcnow() - timestamp.astimezone(datetime.UTC)


# =========================== 用户数据库与登录系统 ===========================

login_manager = LoginManager(app)
login_manager.login_view = 'login'


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
    cmtlastvisit = db.Column(db.DateTime)

    def verify_password(self, password):
        return False if self.password is None else \
            check_password_hash(self.password, password)

    def edit_profile(
            self, name, password, confirmpassword, avatarfile, gender):
        user_exists = db.session.query(
            User.query.filter_by(name=name).exists()).scalar()
        if name != self.name and user_exists:
            return '用户名与其他用户重复。'
        elif password != confirmpassword:
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

    def unread_comments(self):
        return Comment.query.filter(db.and_(
            True if self.cmtlastvisit is None
            else self.cmtlastvisit < Comment.timestamp,
            Comment.replyto.has(Comment.uid == self.uid))).order_by(
            Comment.timestamp.desc()).all()

    def update_cmtlastvisit(self):
        self.cmtlastvisit = _utcnow()
        db.session.commit()

    def url(self):
        return url_for('users', uid=self.uid)

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


def register_user(name, gender, password, confirmpassword, avatarfile):
    user_exists = db.session.query(
        User.query.filter_by(name=name).exists()).scalar()
    if name and password and not user_exists and password == confirmpassword:
        user = User(
            name=name, gender=gender,
            password=generate_password_hash(password))
        if avatarfile is not None:
            user.avatar = avatarfile.read()
            user.avmimetype = mimetypes.guess_type(avatarfile.filename)[0]
        db.session.add(user)
        db.session.commit()
        return True, user
    elif password != confirmpassword:
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

    def get_answer(self):
        if not self.answer:
            return []
        answer = json.loads(self.answer)
        if not isinstance(answer, list):
            answer = [[{}, answer]]
        return answer

    def check_answers(self, userans):
        return check_answers(self.get_answer(), userans)

    def add_submission(self, user, answer):
        answer_eval, testpoints = self.check_answers(answer)
        passedlist = testpoints_passedlist(testpoints)
        submission = Submission(
            user=user, answer=answer, ispassed=all(passedlist),
            score=100 * sum(passedlist) // len(
                passedlist) if passedlist else 0)
        db.session.add(submission)
        submission.prob = self
        db.session.commit()
        return answer_eval, testpoints, submission

    def get_toplevel_comments(self):
        return Comment.query.filter(db.and_(
            Comment.post_type == 'prob', Comment.post_ident == self.probno,
            Comment.replyto_id.is_(None))).order_by(
            Comment.timestamp.desc()).all()

    def edit(self, probtitle, problabels, statement, answer):
        if probtitle:
            self.probtitle = probtitle
        if statement:
            self.statement = statement
        self.answer = answer
        self.problabels = {get_label(labelname) for labelname in problabels}
        db.session.commit()

    def as_labelnames(self):
        return {label.labelname for label in self.problabels}

    def url(self):
        return url_for('probs', probno=self.probno)

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

    def url(self):
        return url_for('solutions', probno=self.probno, solno=self.solno)

    def get_post_ident(self):
        return list2csv([self.probno, self.solno])

    def get_toplevel_comments(self):
        post_ident = self.get_post_ident()
        return Comment.query.filter(db.and_(
            Comment.post_type == 'solution', Comment.post_ident == post_ident,
            Comment.replyto_id.is_(None))).order_by(
            Comment.timestamp.desc()).all()

    def edit(self, title, content):
        if title:
            self.title = title
        if content:
            self.content = content
        db.session.commit()

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

    def to_response(self):
        return Response(self.data, mimetype=self.mimetype)


class ProbLabel(db.Model):
    __tablename__ = 'labels'
    labelname = db.Column(db.String(16), primary_key=True)
    probs = db.relationship(
        'Prob', secondary=prob_label, back_populates='problabels',
        collection_class=set)

    def url(self):
        return url_for('problistoflabel', labelname=self.labelname)


def get_prob(probno):
    if isinstance(probno, str):
        return db.session.get(Prob, probno)


def search_probs(form, extra_req=None):
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
    flag = bool(requirements)
    if extra_req is not None:
        requirements.append(extra_req)
    if not requirements:
        return Prob.query.order_by(Prob.probno.asc()), flag
    return Prob.query.filter(db.and_(*requirements)).order_by(
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
    if isinstance(probno, str) and isinstance(solno, int):
        return db.session.get(ProbSolution, (probno, solno))


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


def get_label(labelname):
    if isinstance(labelname, str):
        return db.session.get(ProbLabel, labelname)


def add2labels(labelnames, prob):
    for labelname in set(labelnames):
        label = get_label(labelname)
        if label is None:
            label = ProbLabel(labelname=labelname)
            db.session.add(label)
        label.probs.add(prob)
    db.session.commit()


# =========================== 讨论区数据库支持 ===========================


class Comment(db.Model):
    __tablename__ = 'comments'
    cmtid = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('users.uid'))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=_utcnow)
    replyto_id = db.Column(db.Integer, db.ForeignKey('comments.cmtid'))
    # 帖子类型为'prob'，标识符为题目编号
    # 帖子类型为'solution'，标识符为CSV格式的题目编号与题解编号的组合
    post_type = db.Column(db.String(16), nullable=False)  # 帖子类型
    post_ident = db.Column(db.Text, nullable=False)       # 帖子标识符
    replyto = db.relationship(
        'Comment', back_populates='replies', remote_side=[cmtid])
    replies = db.relationship(
        'Comment', back_populates='replyto', cascade='all, delete')

    def get_all_replies(self):
        return sorted(sum(
            [comment.get_all_replies() for comment in self.replies],
            start=self.replies.copy()))

    def get_post(self):
        if self.post_type == 'prob':
            return get_prob(self.post_ident)
        elif self.post_type == 'solution':
            probno, solno = csv2list(self.post_ident)
            return get_solution(probno, int(solno))

    def __lt__(self, comment):
        return self.timestamp < comment.timestamp


def get_comment(cmtid):
    if isinstance(cmtid, int):
        return db.session.get(Comment, cmtid)


def clear_comments(post):
    for comment in post.get_toplevel_comments():
        db.session.delete(comment)
    db.session.commit()


# =========================== 讨论区路由 ===========================


@app.route('/post-comment/<post_type>/<post_ident>', methods=['POST'])
@login_required
def post_comment(post_type, post_ident):
    content = request.form.get('commenttext')
    comment = Comment(
        user=current_user, content=content,
        post_type=post_type, post_ident=post_ident)
    db.session.add(comment)
    db.session.commit()
    return redirect(comment.get_post().url())


@app.route(
    '/post-comment/<post_type>/<post_ident>/<int:cmtid>', methods=['POST'])
@login_required
def post_subcomment(post_type, post_ident, cmtid):
    content = request.form.get('commenttext')
    comment = Comment(
        user=current_user, content=content, replyto_id=cmtid,
        post_type=post_type, post_ident=post_ident)
    db.session.add(comment)
    db.session.commit()
    return redirect(comment.get_post().url())


@app.route('/delete-comment', methods=['POST'])
@login_required
def delete_comment():
    cmtid = int(request.form.get('cmtid'))
    comment = get_comment(cmtid)
    if comment and current_user == comment.user:
        db.session.delete(comment)
        db.session.commit()
    return redirect(comment.get_post().url())


@app.route('/unread-comments')
@login_required
def unread_comments():
    return render_template('unread_comments.html')


# =========================== 题目各项网页 ===========================


@app.route('/probs/', methods=['GET', 'POST'])
def problist():
    form = {}
    if request.method == 'POST':
        for key in (
                'probno', 'probtitle', 'statement', 'problabels', 'source'):
            form[key] = request.form.get(key)
    probs, query = search_probs(form)
    return render_template(
        'problist.html', probs=probs, query=query, form=form)


@app.route('/labels/')
def labellist():
    return render_template('labellist.html', labels=ProbLabel.query.all())


@app.route('/labels/<labelname>', methods=['GET', 'POST'])
def problistoflabel(labelname):
    form = {}
    if request.method == 'POST':
        for key in (
                'probno', 'probtitle', 'statement', 'problabels', 'source'):
            form[key] = request.form.get(key)
    probs, query = search_probs(form, Prob.problabels.any(
        ProbLabel.labelname == labelname))
    return render_template(
        'problist.html', labelname=labelname, oflabel=True, form=form,
        probs=probs, query=query)


@app.route('/probs/<probno>')
def probs(probno):
    prob = get_prob(probno)
    if prob:
        return render_template('prob.html', prob=prob)
    return render_template('notfound.html', error='未能找到题目。')


@app.route('/images/<probno>/<imagename>')
def imagefile(probno, imagename):
    image = db.session.get(ProbImage, (probno, imagename))
    return '' if image is None else image.to_response()


@app.route('/probs/<probno>/submit', methods=['POST'])
@login_required
def submit(probno):
    answer = request.form.get('answertext')
    prob = get_prob(probno)
    if not prob:
        return render_template('notfound.html', error='未能找到题目。')
    answer_eval, testpoints, submission = prob.add_submission(
        current_user, answer)
    return render_template(
        'submit.html',
        answer_latex=latex(answer_eval) if answer_eval else None,
        prob=prob, submission=submission, testpoints=testpoints)


@app.route('/probs/<probno>/solutions/<int:solno>')
def solutions(probno, solno):
    solution = get_solution(probno, solno)
    if not solution:
        return render_template('notfound.html', error='未能找到题解。')
    prob = solution.prob
    solutions = prob.solutions.copy()
    solutions.remove(solution)
    suggested = random.sample(solutions, min(len(solutions), 3))
    return render_template(
        'solutions.html', prob=prob, solution=solution, suggested=suggested)


@app.route('/probs/<probno>/edit', methods=['GET', 'POST'])
@login_required
def edit_prob(probno):
    prob = get_prob(probno)
    if not prob:
        return render_template('notfound.html', error='未能找到题目。')
    if current_user != prob.source:
        return redirect(prob.url())
    if request.method == 'POST':
        probtitle = request.form.get('probtitle')
        problabels = [
            labelname.replace(' ', '')
            for labelname in csv2list(request.form.get('problabels'))]
        statement = request.form.get('statement')
        answers = request.form.get('answers')
        imgfiles = request.files.getlist('imgfiles')
        error = add_images(probno, imgfiles)
        if error is not None:
            return render_template(
                'upload_prob.html', editmode=True, prob=prob, error=error)
        prob.edit(probtitle, problabels, statement, answers)
        return redirect(prob.url())
    return render_template('upload_prob.html', editmode=True, prob=prob)


@app.route(
    '/probs/<probno>/solutions/<int:solno>/edit', methods=['GET', 'POST'])
@login_required
def edit_solution(probno, solno):
    solution = get_solution(probno, solno)
    if not solution:
        return render_template('notfound.html', error='未能找到题解。')
    if current_user != solution.user:
        return redirect(solution.url())
    if request.method == 'POST':
        soltitle = request.form.get('soltitle')
        content = request.form.get('solution')
        imgfiles = request.files.getlist('imgfiles')
        error = add_images(probno, imgfiles)
        if error is not None:
            return render_template(
                'upload_solution.html', editmode=True,
                prob=solution.prob, solution=solution, error=error)
        solution.edit(soltitle, content)
        return redirect(solution.url())
    return render_template(
        'upload_solution.html', editmode=True,
        prob=solution.prob, solution=solution)


@app.route('/upload-prob', methods=['GET', 'POST'])
@login_required
def upload_prob():
    if request.method == 'POST':
        probno = request.form.get('probno')
        probtitle = request.form.get('probtitle')
        problabels = [
            labelname.replace(' ', '')
            for labelname in csv2list(request.form.get('problabels'))]
        statement = request.form.get('statement')
        answers = request.form.get('answers')
        imgfiles = request.files.getlist('imgfiles')
        error = add_images(probno, imgfiles)
        if error is not None:
            return render_template(
                'upload_prob.html', probno=probno, probtitle=probtitle,
                problabels=request.form.get('problabels'),
                statement=statement, answers=answers, error=error)
        status, prob = add_prob(
            probno=probno, probtitle=probtitle,
            statement=statement, answer=answers, source=current_user)
        if not status:
            return render_template(
                'upload_prob.html', probno=probno, probtitle=probtitle,
                problabels=request.form.get('problabels'),
                statement=statement, answers=answers, error=prob)
        add2labels(problabels, prob)
        return redirect(prob.url())
    return render_template('upload_prob.html')


@app.route('/probs/<probno>/upload-solution', methods=['GET', 'POST'])
@login_required
def upload_solution(probno):
    prob = get_prob(probno)
    if not prob:
        return render_template('notfound.html', error='未能找到题目。')
    if request.method == 'POST':
        soltitle = request.form.get('soltitle')
        content = request.form.get('solution')
        imgfiles = request.files.getlist('imgfiles')
        error = add_images(probno, imgfiles)
        if error is not None:
            return render_template(
                'upload_solution.html', prob=prob,
                soltitle=soltitle, content=content, error=error)
        status, solution = add_solution(probno, soltitle, content)
        if not status:
            return render_template(
                'upload_solution.html', prob=prob,
                soltitle=soltitle, content=content, error=solution)
        return redirect(solution.url())
    return render_template('upload_solution.html', prob=prob)


@app.route('/probs/<probno>/delete')
@login_required
def delete_prob(probno):
    prob = get_prob(probno)
    if not prob:
        return render_template('notfound.html', error='未能找到题目。')
    if current_user == prob.source:
        prob.problabels.clear()
        clear_comments(prob)
        db.session.delete(prob)
        db.session.commit()
        return redirect(url_for('welcome'))
    return redirect(prob.url())


@app.route('/probs/<probno>/solutions/<int:solno>/delete')
@login_required
def delete_solution(probno, solno):
    solution = get_solution(probno, solno)
    if not solution:
        return render_template('notfound.html', error='未能找到题解。')
    if current_user == solution.user:
        clear_comments(solution)
        db.session.delete(solution)
        db.session.commit()
        return redirect(url_for('probs', probno=probno))
    return redirect(solution.url())


# =========================== 登录系统网页 ===========================


@app.route('/')
def home():
    return redirect(url_for('welcome'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = find_user(username, 'name')
        if user is not None and user.verify_password(password):
            login_user(user, remember=True)
            return redirect(url_for('welcome'))
        else:
            error = '用户名或密码错误。'
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        name = request.form.get('username')
        gender = int(request.form.get('gender'))
        password = request.form.get('password')
        confirmpassword = request.form.get('confirmpassword')
        avatar = request.files.get('avatar')
        status, user = register_user(
            name, gender, password, confirmpassword, avatar)
        if status:
            login_user(user, remember=True)
            return redirect(url_for('welcome'))
        error = user
    return render_template('register.html', error=error)


@app.route('/welcome')
@login_required
def welcome():
    return render_template('welcome.html', user=current_user)


@app.route('/users/<int:uid>')
def users(uid):
    user = find_user(uid)
    if user:
        return render_template('welcome.html', user=find_user(uid))
    return render_template('notfound.html', error='未能找到用户。')


@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirmpassword = request.form.get('confirmpassword')
        avatar = request.files.get('avatar')
        gender = int(request.form.get('gender'))
        error = current_user.edit_profile(
            username, password, confirmpassword, avatar, gender)
        if error is None:
            return redirect(url_for('welcome'))
    return render_template('edit_profile.html', error=error)


@app.route('/edit-introduction', methods=['POST'])
@login_required
def edit_introduction():
    introduction = request.form.get('introduction')
    current_user.introduction = introduction
    db.session.commit()
    return redirect(url_for('welcome'))


@app.route('/avatars/<int:uid>')
def avatarfile(uid):
    user = find_user(uid)
    if not user or not user.avatar:
        return '', 404  # 未找到
    if not user.avlastmodified:
        user.avlastmodified = datetime.datetime.min
        db.session.commit()
    etag = hashlib.md5(user.avatar).hexdigest()
    if_none_match = request.headers.get('If-None-Match')
    if_modified_since = request.headers.get('If-Modified-Since')
    if if_none_match and if_none_match == etag:
        return '', 304
    if if_modified_since:
        try:
            client_time = datetime.datetime.strptime(
                if_modified_since, '%a, %d %b %Y %H:%M:%S GMT')
            if client_time >= user.avlastmodified.replace(microsecond=0):
                return '', 304
        except ValueError:
            return '', 400  # 时间格式错误，无法处理
    response = make_response(user.avatar)
    response.headers['Content-Type'] = user.avmimetype or 'image/jpeg'
    response.headers['ETag'] = etag
    response.headers['Last-Modified'] = user.avlastmodified.strftime(
        '%a, %d %b %Y %H:%M:%S GMT')
    response.headers['Cache-Control'] = 'public, max-age=600'  # 缓存10min
    return response


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/unregister')
@login_required
def unregister():
    unregister_user(current_user)
    logout_user()
    return redirect(url_for('home'))


app.jinja_env.add_extension('jinja2.ext.do')
app.add_template_global(list2csv, 'list2csv')
app.add_template_global(_utcfromnow, 'utcfromnow')
app.add_template_global(datetime.timedelta, 'timedelta')
app.add_template_global(TPStatus, 'TPStatus')
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
