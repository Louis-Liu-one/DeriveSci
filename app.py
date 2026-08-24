'''
Copyright (c) 2026 Louis Liu  All rights reserved.

我们的网站支持如下的路由。

用户操作页面：
/                           首页（未登录）/欢迎页（已登录）
/home                       首页
/welcome                    欢迎页
/login                      登录
/register                   注册
/edit-profile               编辑信息
/users/<uid>                查看他人主页
/api/user/login             登录
/api/user/register          注册
/api/user/logout            退出
/api/user/unregister        注销
/api/user/edit-profile      编辑个人资料
/api/user/edit-introduction 编辑个人简介

私信与评论页面：
/chat                      私信聊天
/api/comment/post          发表评论
/api/comment/delete        删除评论
/api/chat/update-lastvisit 更新上次查看私信的时间
/api/chat/send             发送私信
/api/chat/messages         获取新收到的私信

帮助页面：
/helps/        查看帮助列表
/helps/<howto> 查看帮助

标签、题集与题目页面：
/tags/                   所有标签
/tags/<tagtitle>         单个标签
/upload-prob             上传题目
/probs/                  题集
/probs/collections/<probno>          题目
/probs/collections/<probno>/submit   提交答案
/probs/collections/<probno>/edit     编辑题目
/api/prob/upload         上传题目
/api/prob/set-official   将题目添加到官方题集
/api/prob/review         通过/拒绝题目的审核
/api/prob/review-comment 保存审核意见
/api/prob/edit           编辑题目
/api/prob/delete         删除题目
/api/prob/search-content 搜索题目内容

题解页面：
/probs/collections/<probno>/upload-solution        上传题解
/probs/collections/<probno>/solutions/<solno>      查看题解
/probs/collections/<probno>/solutions/<solno>/edit 编辑题解
/api/solution/upload                   上传题解
/api/solution/edit                     编辑题解
/api/solution/delete                   删除题解

专栏页面：
/upload-article             撰写专栏
/articles/<article_id>      阅读专栏
/articles/<article_id>/edit 编辑专栏
/api/article/upload         上传专栏
/api/article/edit           编辑专栏
/api/article/delete         删除专栏

图片页面：
/images/<post_type>/<post_ident>                 图片列表
/images/<post_type>/<post_ident>/<filename>      图片
/images/<post_type>/<post_ident>/<filename>/view 图片预览
/api/image/reupload                              重新上传图片
/api/image/rename                                重命名图片
/api/image/delete                                删除图片


以/api/开头的路由是 API 路由。
'''

import os

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_moment import Moment

from models import db, init_app, auto_format_time, find_user
from anschecker import TPStatus
from blueprints import register_all

load_dotenv(override=True)
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
init_app(app)
moment = Moment(app)

register_all(app)


@app.route('/')
def home():
    from flask_login import current_user
    from flask import redirect, url_for, render_template
    if current_user.is_authenticated:
        return redirect(url_for('auth.welcome'))
    return render_template('homepage.html')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('notfound.html', error='未能找到页面。'), 404


app.jinja_env.add_extension('jinja2.ext.do')
app.add_template_global(find_user, 'find_user')
app.add_template_global(auto_format_time, 'auto_format_time')
app.add_template_global(TPStatus, 'TPStatus')
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
