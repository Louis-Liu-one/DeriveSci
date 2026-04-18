'''MathProbsOnline.PythonAnyWhere.com
Copyright (c) 2026 Louis Liu  All rights reserved.

我们的网站支持如下的路由。

用户操作：
/login         登录
/register      注册
/edit-profile  编辑信息
/users/<uid>   查看他人主页
/helps/        查看帮助列表
/helps/<howto> 查看帮助
/chat          私信聊天

题目：
/upload-prob                           上传题目
/labels/                               所有标签
/labels/<labelname>                    单个标签
/probs/                                题集
/probs/<probno>                        题目<probno>
/probs/<probno>/submit                 提交题目<probno>的答案*
/probs/<probno>/edit                   编辑题目
/probs/<probno>/upload-solution        上传题解
/probs/<probno>/solutions/<solno>      查看题解
/probs/<probno>/solutions/<solno>/edit 编辑题解
/images/<probno>/<filename>            题目/题解图片

API：*
/api/prob/upload            上传题目
/api/prob/set-official      将题目添加到官方题集
/api/prob/review            通过/拒绝题目的审核
/api/prob/edit              编辑题目
/api/prob/delete            删除题目
/api/solution/upload        上传题解
/api/solution/edit          编辑题解
/api/solution/delete        删除题解
/api/comment/post           发表评论
/api/comment/delete         删除评论
/api/chat/update-lastvisit  更新上次查看私信的时间
/api/chat/send              发送私信
/api/chat/messages          获取新收到的私信
/api/user/login             登录
/api/user/register          注册
/api/user/logout            登出
/api/user/unregister        注销
/api/user/edit-profile      编辑个人资料
/api/user/edit-introduction 编辑个人简介

标*的是使用 POST 方法的路由，所有 API 路由仅限 POST 方法。

已部署至：https://MathProbsOnline.PythonAnyWhere.com
'''

import os
import json
import random
import hashlib
import datetime

from flask import Flask, request, jsonify, abort, url_for, redirect
from flask import render_template, render_template_string, make_response
from flask_login import current_user, login_required, login_user, logout_user
from flask_moment import Moment, moment as builtin_moment

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


@app.errorhandler(404)
def page_not_found(error):
    return render_template('notfound.html', error='未能找到页面。'), 404


# =========================== 讨论区各路由与API ===========================


@app.route('/api/comment/delete', methods=['POST'])
def api_delete_comment():
    if not current_user.is_authenticated:
        return {'ok': False, 'error': '用户未登录。'}, 401
    commentid = int(request.json.get('commentid'))
    comment = get_comment(commentid)
    if not comment:
        return {'ok': False, 'error': '未找到评论，此条评论可能已被删除。'}, 404
    if not comment.editable_for(current_user):
        abort(403)  # 无删除评论的权限
    db.session.delete(comment)
    db.session.commit()
    return {'ok': True}


@app.route('/api/comment/post', methods=['POST'])
def api_post_comment():
    if not current_user.is_authenticated:
        return {'ok': False, 'error': '用户未登录。'}, 401
    data = request.json
    post_type = data.get('post_type')
    post_ident = data.get('post_ident')
    content = data.get('content')
    replyto_id = data.get('replyto_id')
    if not content:
        return {'ok': False, 'error': '评论内容不能为空。'}, 400
    comment = Comment(
        user=current_user, content=content,
        post_type=post_type, post_ident=post_ident,
        replyto_id=replyto_id)
    db.session.add(comment)
    db.session.commit()
    # 渲染评论HTML，直接使用内联模板字符串
    rendered_html = render_template_string(
        '{% from "includes/comment.html" import commentdiv with context %}'
        '{{ commentdiv(comment, toplevel=toplevel, '
        'secondlevel=secondlevel) }}', comment=comment,
        toplevel=not bool(replyto_id), secondlevel=bool(replyto_id)
        and comment.replyto and not comment.replyto.replyto_id,
        moment=builtin_moment)
    return {'ok': True, 'html': rendered_html, 'is_reply': bool(replyto_id)}


# =========================== 题目各项网页与API ===========================


@app.route('/probs/', methods=['GET', 'POST'])
def problist():
    reviewmode = request.args.get('reviewmode') == 'True'
    if reviewmode and not (
            current_user.is_authenticated and current_user.isadmin):
        return redirect(url_for('problist'))
    form = {}
    keys = 'probno', 'probtitle', 'statement', 'problabels', 'source', \
        'probtype', 'review_status' if reviewmode else ''
    if request.method == 'POST':
        for key in keys:
            form[key] = request.form.get(key)
    probs, query = search_probs(form, reviewmode=reviewmode)
    return render_template(
        'problist.html', reviewmode=reviewmode,
        probs=probs, query=query, form=form)


@app.route('/labels/')
def labellist():
    return render_template('labellist.html', labels=ProbLabel.query.all())


@app.route('/labels/<labelname>', methods=['GET', 'POST'])
def problistoflabel(labelname):
    form = {}
    keys = 'probno', 'probtitle', 'statement', \
        'problabels', 'source', 'probtype'
    if request.method == 'POST':
        for key in keys:
            form[key] = request.form.get(key)
    probs, query = search_probs(form, Prob.problabels.any(
        ProbLabel.labelname == labelname))
    return render_template(
        'problist.html', labelname=labelname, oflabel=True, form=form,
        probs=probs, query=query)


@app.route('/probs/<probno>')
def probs(probno):
    prob = get_prob(probno)
    if prob and prob.viewable_for(current_user):
        return render_template('prob.html', prob=prob)
    return render_template('notfound.html', error='未能找到题目。'), 404


@app.route('/images/<probno>/<imagename>')
def imagefile(probno, imagename):
    image = db.session.get(ProbImage, (probno, imagename))
    if not image:
        abort(404)  # 未找到
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
    if not prob or not prob.viewable_for(current_user):
        return render_template('notfound.html', error='未能找到题目。'), 404
    answer_eval, testpoints, submission = prob.add_submission(
        current_user, answer)
    return render_template(
        'submit.html',
        answer_latex=latex(answer_eval) if answer_eval else None,
        prob=prob, submission=submission, testpoints=testpoints)


@app.route('/probs/<probno>/solutions/<int:solno>')
def solutions(probno, solno):
    solution = get_solution(probno, solno)
    if not solution or not solution.viewable_for(current_user):
        return render_template('notfound.html', error='未能找到题解。'), 404
    prob = solution.prob
    solutions = prob.solutions.copy()
    solutions.remove(solution)
    suggested = random.sample(solutions, min(len(solutions), 3))
    return render_template(
        'solution.html', prob=prob, solution=solution, suggested=suggested)


@app.route('/probs/<probno>/edit')
@login_required
def edit_prob(probno):
    prob = get_prob(probno)
    if not prob:
        return render_template('notfound.html', error='未能找到题目。'), 404
    if not prob.editable_for(current_user):
        return redirect(prob.url())
    return render_template('upload_prob.html', editmode=True, prob=prob)


@app.route('/probs/<probno>/solutions/<int:solno>/edit')
@login_required
def edit_solution(probno, solno):
    solution = get_solution(probno, solno)
    if not solution or not solution.viewable_for(current_user):
        return render_template('notfound.html', error='未能找到题解。'), 404
    if current_user != solution.user and not current_user.isadmin:
        return redirect(solution.url())
    return render_template(
        'upload_solution.html', editmode=True,
        prob=solution.prob, solution=solution)


@app.route('/upload-prob')
@login_required
def upload_prob():
    return render_template('upload_prob.html')


@app.route('/probs/<probno>/upload-solution')
@login_required
def upload_solution(probno):
    prob = get_prob(probno)
    if not prob:
        return render_template('notfound.html', error='未能找到题目。'), 404
    return render_template('upload_solution.html', prob=prob)


@app.route('/api/prob/upload', methods=['POST'])
def api_upload_prob():
    if not current_user.is_authenticated:
        return {'ok': False, 'error': '用户未登录。'}, 401
    probno = request.form.get('probno')
    probtitle = request.form.get('probtitle')
    problabels = json.loads(request.form.get('problabels', '[]'))
    statement = request.form.get('statement')
    answers = request.form.get('answers')
    imgfiles = request.files.getlist('imgfiles')
    isofficial = current_user.isadmin and request.form.get(
        'isofficial') == 'on'
    review_status = 1 if current_user.isadmin else -1
    error = add_images(probno, imgfiles)
    if error is not None:
        return {'ok': False, 'error': str(error)}, 400
    status, prob = add_prob(
        probno=probno, probtitle=probtitle, statement=statement,
        answer=answers, source=current_user,
        review_status=review_status, isofficial=isofficial)
    if not status:
        return {'ok': False, 'error': str(prob)}, 400
    add2labels(problabels, prob)
    return {'ok': True, 'url': prob.url()}


@app.route('/api/prob/edit', methods=['POST'])
def api_edit_prob():
    if not current_user.is_authenticated:
        return {'ok': False, 'error': '用户未登录。'}, 401
    probno = request.form.get('probno')
    prob = get_prob(probno)
    if not prob:
        return {'ok': False, 'error': '未能找到题目。'}, 404
    if not prob.editable_for(current_user):
        abort(403)  # 无编辑权限
    probtitle = request.form.get('probtitle')
    problabels = json.loads(request.form.get('problabels', '[]'))
    statement = request.form.get('statement')
    answers = request.form.get('answers')
    imgfiles = request.files.getlist('imgfiles')
    error = add_images(probno, imgfiles)
    if error is not None:
        return {'ok': False, 'error': str(error)}, 400
    prob.edit(probtitle, problabels, statement, answers)
    return {'ok': True, 'url': prob.url()}


@app.route('/api/prob/review', methods=['POST'])
def api_review_prob():
    if not current_user.is_authenticated:
        return {'ok': False, 'error': '用户未登录。'}, 401
    if not current_user.isadmin:
        abort(403)  # 无审核题目的权限
    probno = request.json.get('probno')
    accept = bool(request.json.get('accept'))
    prob = get_prob(probno)
    if not prob:
        return {'ok': False, 'error': '未能找到题目。'}, 404
    prob.review_status = 1 if accept else 0
    db.session.commit()
    return {
        'ok': True, 'accept': accept,
        'url': prob.url() if accept else url_for('problist')}


@app.route('/api/prob/set-official', methods=['POST'])
def api_set_official_prob():
    if not current_user.is_authenticated:
        return {'ok': False, 'error': '用户未登录。'}, 401
    if not current_user.isadmin:
        abort(403)  # 无编辑官方题集的权限
    probno = request.json.get('probno')
    prob = get_prob(probno)
    if not prob:
        return {'ok': False, 'error': '未能找到题目。'}, 404
    prob.isofficial = not prob.isofficial
    db.session.commit()
    return {'ok': True, 'isofficial': prob.isofficial}


@app.route('/api/prob/delete', methods=['POST'])
def api_delete_prob():
    if not current_user.is_authenticated:
        return {'ok': False, 'error': '用户未登录。'}, 401
    probno = request.json.get('probno')
    prob = get_prob(probno)
    if not prob or not prob.viewable_for(current_user):
        return {'ok': False, 'error': '未能找到题目。'}, 404
    if not prob.editable_for(current_user):
        abort(403)  # 无删除权限
    prob.problabels.clear()
    clear_comments(prob)
    db.session.delete(prob)
    db.session.commit()
    return {'ok': True, 'url': url_for('problist')}


@app.route('/api/solution/upload', methods=['POST'])
def api_upload_solution():
    if not current_user.is_authenticated:
        return {'ok': False, 'error': '用户未登录。'}, 401
    probno = request.form.get('probno')
    prob = get_prob(probno)
    if not prob:
        return {'ok': False, 'error': '未能找到题目。'}, 404
    soltitle = request.form.get('soltitle')
    content = request.form.get('solution')
    imgfiles = request.files.getlist('imgfiles')
    error = add_images(probno, imgfiles)
    if error is not None:
        return {'ok': False, 'error': str(error)}, 400
    status, solution = add_solution(probno, soltitle, content)
    if not status:
        return {'ok': False, 'error': str(solution)}, 400
    return {'ok': True, 'url': solution.url()}


@app.route('/api/solution/edit', methods=['POST'])
def api_edit_solution():
    if not current_user.is_authenticated:
        return {'ok': False, 'error': '用户未登录。'}, 401
    probno, solno = request.form.get('probno'), int(request.form.get('solno'))
    solution = get_solution(probno, solno)
    if not solution or not solution.viewable_for(current_user):
        return {'ok': False, 'error': '未能找到题解。'}, 404
    if not solution.editable_for(current_user):
        abort(403)  # 无修改权限
    soltitle = request.form.get('soltitle')
    content = request.form.get('solution')
    imgfiles = request.files.getlist('imgfiles')
    error = add_images(probno, imgfiles)
    if error is not None:
        return {'ok': False, 'error': str(error)}, 400
    solution.edit(soltitle, content)
    return {'ok': True, 'url': solution.url()}


@app.route('/api/solution/delete', methods=['POST'])
def api_delete_solution():
    if not current_user.is_authenticated:
        return {'ok': False, 'error': '用户未登录。'}, 401
    probno, solno = request.json.get('probno'), int(request.json.get('solno'))
    solution = get_solution(probno, solno)
    prob_url = solution.prob.url()
    if not solution or not solution.viewable_for(current_user):
        return {'ok': False, 'error': '未能找到题解。'}, 404
    if not solution.editable_for(current_user):
        abort(403)  # 无删除权限
    clear_comments(solution)
    db.session.delete(solution)
    db.session.commit()
    return {'ok': True, 'url': prob_url}


@app.route('/helps/<howto>')
def helps(howto):
    if not howto.endswith('.md'):
        howto += '.md'
    path = os.path.join(app.root_path, app.template_folder, 'helps', howto)
    if os.path.exists(path):
        return render_template(
            'helps.html', filename=os.path.join('helps', howto))
    return render_template('notfound.html', error='未能找到帮助文档。'), 404


@app.route('/helps/')
def helplist():
    return render_template('helplist.html')


# =========================== 用户操作网页与API ===========================


@app.route('/')
def home():
    return render_template('homepage.html')


@app.route('/api/user/login', methods=['POST'])
def api_user_login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = find_user(username, 'name')
    if user is not None and user.verify_password(password):
        login_user(user, remember=True)
        return {'ok': True}
    return {'ok': False, 'error': '用户名或密码错误。'}, 400


@app.route('/api/user/register', methods=['POST'])
def api_user_register():
    name = request.form.get('username')
    gender = int(request.form.get('gender'))
    password = request.form.get('password')
    password_confirmation = request.form.get('password_confirmation')
    avatar = request.files.get('avatar')
    status, user = register_user(
        name, gender, password, password_confirmation, avatar)
    if status:
        login_user(user, remember=True)
        return {'ok': True}
    return {'ok': False, 'error': str(user)}, 400


@app.route('/login')
def login():
    nextpage = request.args.get('next')
    if not nextpage:
        nextpage = url_for('welcome')
    return render_template('login.html', next=nextpage)


@app.route('/register')
def register():
    nextpage = request.args.get('next')
    if not nextpage:
        nextpage = url_for('welcome')
    return render_template('register.html', next=nextpage)


@app.route('/welcome')
@login_required
def welcome():
    return render_template('welcome.html', user=current_user)


@app.route('/users/<int:uid>')
def users(uid):
    user = find_user(uid)
    if user:
        return render_template('welcome.html', user=find_user(uid))
    return render_template('notfound.html', error='未能找到用户。'), 404


@app.route('/chat')
@login_required
def chat():
    view_comments = request.args.get('view_comments', 'False') == 'True'
    if view_comments:
        return render_template('chat.html', view_comments=True)
    activeuid = request.args.get('activeuid')
    return render_template('chat.html', activeuser=find_user(activeuid))


@app.route('/api/chat/update-lastvisit', methods=['POST'])
def api_chat_update_lastvisit():
    try:
        receiver_uid = request.json.get('receiver_uid')
        sender_uid = request.json.get('sender_uid')
        if not receiver_uid or not sender_uid:
            return {'ok': False, 'error': '未能找到用户。'}, 400
        update_chatlastvisit(receiver_uid, sender_uid)
        return {'ok': True}
    except BaseException as err:
        return {'ok': False, 'error': str(err)}, 400


@app.route('/api/chat/send', methods=['POST'])
def api_chat_send():
    try:
        receiver_uid = request.json.get('receiver_uid')
        sender_uid = request.json.get('sender_uid')
        message = request.json.get('message')
        find_user(sender_uid).chat_to(receiver_uid, message)
        return {'ok': True}
    except BaseException as err:
        return {'ok': False, 'error': str(err)}, 400


@app.route('/api/chat/messages', methods=['POST'])
def api_chat_messages():
    try:
        receiver_uid = int(request.json.get('receiver_uid'))
        lastmsgtime = request.json.get('lastmsgtime')
        return jsonify(find_user(receiver_uid).all_chats(
            datetime.datetime.fromisoformat(
                lastmsgtime)) if lastmsgtime else None)
    except BaseException as err:
        return {}, 400


@app.route('/api/user/edit-profile', methods=['POST'])
def api_edit_profile():
    if not current_user.is_authenticated:
        return {'ok': False, 'error': '用户未登录。'}, 401
    username = request.form.get('username')
    password = request.form.get('password')
    password_confirmation = request.form.get('password_confirmation')
    avatar = request.files.get('avatar')
    gender = int(request.form.get('gender'))
    error = current_user.edit_profile(
        username, password, password_confirmation, avatar, gender)
    if error is None:
        return {'ok': True, 'url': url_for('welcome')}
    return {'ok': False, 'error': str(error)}, 400


@app.route('/api/user/edit-introduction', methods=['POST'])
def api_edit_introduction():
    if not current_user.is_authenticated:
        return {'ok': False, 'error': '用户未登录。'}, 401
    introduction = request.json.get('introduction')
    current_user.introduction = introduction
    db.session.commit()
    return {'ok': True}


@app.route('/edit-profile')
@login_required
def edit_profile():
    return render_template('edit_profile.html')


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
        return '', 304  # 已缓存
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


@app.route('/api/user/logout', methods=['POST'])
def api_user_logout():
    if not current_user.is_authenticated:
        return {'ok': False, 'error': '用户未登录。'}, 401
    logout_user()
    return {'ok': True, 'url': url_for('home')}, 400


@app.route('/api/user/unregister', methods=['POST'])
def api_user_unregister():
    if not current_user.is_authenticated:
        return {'ok': False, 'error': '用户未登录。'}, 401
    try:
        unregister_user(current_user)
        logout_user()
        return {'ok': True, 'url': url_for('home')}
    except Exception as err:
        return {'ok': False, 'error': str(err)}, 400


app.jinja_env.add_extension('jinja2.ext.do')
app.add_template_global(get_helplist(), 'helplist')
app.add_template_global(find_user, 'find_user')
app.add_template_global(utcfromnow, 'utcfromnow')
app.add_template_global(datetime.timedelta, 'timedelta')
app.add_template_global(TPStatus, 'TPStatus')
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
