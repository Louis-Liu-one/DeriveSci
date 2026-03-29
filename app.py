'''MathProbsOnline.PythonAnyWhere.com
Copyright (c) 2026 Louis Liu  All rights reserved.

我们的网站支持如下的路由。

用户操作：
/login             登录
/logout            登出*
/register          注册
/unregister        注销*
/edit-profile      编辑信息
/edit-introduction 编辑简介*
/users/<uid>       查看他人主页
/helps/            查看帮助列表
/helps/<howto>     查看帮助
/chat              私信聊天
/post-comment/<post_type>/<post_ident>         发表评论*
/post-comment/<post_type>/<post_ident>/<cmtid> 回复评论*
/delete-comment                                删除评论*

题目：
/upload-prob         上传题目
/labels/             所有标签
/labels/<labelname>  单个标签
/probs/              题集
/probs/<probno>                 题目<probno>
/probs/<probno>/submit          提交题目<probno>的答案*
/probs/<probno>/edit            编辑题目
/probs/<probno>/delete          删除题目*
/probs/<probno>/upload-solution 上传题解
/probs/<probno>/solutions/<solno>        查看题解
/probs/<probno>/solutions/<solno>/edit   编辑题解
/probs/<probno>/solutions/<solno>/delete 删除题解*
/images/<probno>/<filename>              题目/题解图片

API：*
/api/chat/update-lastvisit 更新上次查看私信的时间
/api/chat/send             发送私信
/api/chat/messages         获取新收到的私信

标*的是无法通过输入网址查看的路由。

已部署至：MathProbsOnline.PythonAnyWhere.com
'''

import os
import random
import hashlib
import datetime

from flask import Flask, request, jsonify, url_for
from flask import render_template, redirect, make_response
from flask_login import current_user, login_required, login_user, logout_user
from flask_moment import Moment

from models import *
from anschecker import TPStatus, latex


app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY')
init_app(app)
moment = Moment(app)


def get_helplist():
    helppath = os.path.join(app.root_path, app.template_folder, 'helps')
    helplist = []
    for filename in os.listdir(helppath):
        if filename.endswith('.md'):
            with open(os.path.join(helppath, filename)) as file:
                title = file.readline().strip()
                if title.startswith('# '):
                    helplist.append((filename[:-3], title[2:]))
    return sorted(helplist)


# =========================== 讨论区路由 ===========================


@app.route('/post-comment/<int:post_type>/<post_ident>', methods=['POST'])
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
    '/post-comment/<int:post_type>/<post_ident>/<int:cmtid>',
    methods=['POST'])
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
    if not image:
        return '', 404  # 未找到
    etag = hashlib.md5(image.data).hexdigest()
    if_none_match = request.headers.get('If-None-Match')
    if if_none_match and if_none_match == etag:
        return '', 304
    response = make_response(image.data)
    response.headers['Content-Type'] = image.mimetype
    response.headers['ETag'] = etag
    response.headers['Cache-Control'] = 'public, max-age=600'  # 缓存10min
    return response


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


@app.route('/helps/<howto>')
def helps(howto):
    if not howto.endswith('.md'):
        howto += '.md'
    path = os.path.join(app.root_path, app.template_folder, 'helps', howto)
    if os.path.exists(path):
        return render_template(
            'helps.html', filename=os.path.join('helps', howto))
    return render_template('notfound.html', error='未能找到帮助文档。')


@app.route('/helps/')
def helplist():
    return render_template('helplist.html')


# =========================== 登录系统网页 ===========================


@app.route('/')
def home():
    return redirect(url_for('welcome'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error, nextpage = None, request.args.get('next')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = find_user(username, 'name')
        if user is not None and user.verify_password(password):
            login_user(user, remember=True)
            return redirect(nextpage if nextpage else url_for('welcome'))
        else:
            error = '用户名或密码错误。'
    return render_template('login.html', next=nextpage, error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    error, nextpage = None, request.args.get('next')
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
            return redirect(nextpage if nextpage else url_for('welcome'))
        error = user
    return render_template('register.html', next=nextpage, error=error)


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


@app.route('/chat')
@login_required
def chat():
    view_comments = request.args.get('view_comments')
    if view_comments:
        return render_template('chat.html', view_comments=True)
    activeuid = request.args.get('activeuid')
    return render_template('chat.html', activeuser=find_user(activeuid))


@app.route('/api/chat/update-lastvisit', methods=['POST'])
def api_chat_update_lastvisit():
    try:
        receiver_uid = request.json.get('receiver_uid')
        sender_uid = request.json.get('sender_uid')
        update_chatlastvisit(receiver_uid, sender_uid)
        return {'ok': True}
    except BaseException as err:
        return {'ok': False, 'error': str(err)}


@app.route('/api/chat/send', methods=['POST'])
def api_chat_send():
    try:
        receiver_uid = request.json.get('receiver_uid')
        sender_uid = request.json.get('sender_uid')
        message = request.json.get('message')
        find_user(sender_uid).chat_to(receiver_uid, message)
        return {'ok': True}
    except BaseException as err:
        return {'ok': False, 'error': str(err)}


@app.route('/api/chat/messages', methods=['POST'])
def api_chat_messages():
    try:
        receiver_uid = int(request.json.get('receiver_uid'))
        lastmsgtime = request.json.get('lastmsgtime')
        return jsonify(find_user(receiver_uid).all_chats(
            datetime.datetime.fromisoformat(lastmsgtime)))
    except BaseException as err:
        return jsonify({})


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
                return '', 304  # 已缓存
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
app.add_template_global(get_helplist(), 'helplist')
app.add_template_global(find_user, 'find_user')
app.add_template_global(utcfromnow, 'utcfromnow')
app.add_template_global(datetime.timedelta, 'timedelta')
app.add_template_global(TPStatus, 'TPStatus')
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
