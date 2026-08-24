"""
Copyright (c) 2026 Louis Liu  All rights reserved.
Copyright (c) 2026 Zatursure  All rights reserved.

网站基础设施相关路由：
/auth/                        网站首页
/auth/home                    网站首页
/auth/login                   用户登录页面
/auth/register                用户注册页面
/auth/welcome                 用户欢迎页面
/auth/users/<int:uid>         用户个人主页
/auth/edit-profile            编辑用户资料页面
/auth/avatars/<int:uid>       用户头像文件

/api/user/login               用户登录（接口）
/api/user/register            用户注册（接口）
/api/user/edit-profile        编辑用户资料（接口）
/api/user/edit-introduction   编辑用户简介（接口）
/api/user/logout              用户登出（接口）
/api/user/unregister          注销用户（接口）
"""

import hashlib
import datetime

from flask import Blueprint, request, url_for, redirect, render_template, make_response
from flask_login import current_user, login_required, login_user, logout_user

from models import db, find_user, register_user, unregister_user

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def register_auth_api(app):

    @app.route("/api/user/login", methods=["POST"])
    def api_user_login():
        username = request.form.get("username")
        password = request.form.get("password")
        user = find_user(username, "name")
        if user is not None and user.verify_password(password):
            login_user(user, remember=True)
            return {"ok": True}
        return {"ok": False, "error": "用户名或密码错误。"}, 400

    @app.route("/api/user/register", methods=["POST"])
    def api_user_register():
        name = request.form.get("username")
        gender = int(request.form.get("gender"))
        password = request.form.get("password")
        password_confirmation = request.form.get("password_confirmation")
        avatar = request.files.get("avatar")
        status, user = register_user(
            name, gender, password, password_confirmation, avatar
        )
        if status:
            login_user(user, remember=True)
            return {"ok": True}
        return {"ok": False, "error": str(user)}, 400

    @app.route("/api/user/edit-profile", methods=["POST"])
    def api_edit_profile():
        if not current_user.is_authenticated:
            return {"ok": False, "error": "用户未登录。"}, 401
        username = request.form.get("username")
        password = request.form.get("password")
        password_confirmation = request.form.get("password_confirmation")
        avatar = request.files.get("avatar")
        gender = int(request.form.get("gender"))
        error = current_user.edit_profile(
            username, password, password_confirmation, avatar, gender
        )
        if error is None:
            return {"ok": True, "url": url_for("auth.welcome")}
        return {"ok": False, "error": str(error)}, 400

    @app.route("/api/user/edit-introduction", methods=["POST"])
    def api_edit_introduction():
        if not current_user.is_authenticated:
            return {"ok": False, "error": "用户未登录。"}, 401
        introduction = request.json.get("introduction")
        current_user.introduction = introduction
        db.session.commit()
        return {"ok": True}

    @app.route("/api/user/logout", methods=["POST"])
    def api_user_logout():
        if not current_user.is_authenticated:
            return {"ok": False, "error": "用户未登录。"}, 401
        logout_user()
        return {"ok": True, "url": url_for("auth.home")}, 400

    @app.route("/api/user/unregister", methods=["POST"])
    def api_user_unregister():
        if not current_user.is_authenticated:
            return {"ok": False, "error": "用户未登录。"}, 401
        try:
            unregister_user(current_user)
            logout_user()
            return {"ok": True, "url": url_for("auth.home")}
        except Exception as err:
            return {"ok": False, "error": str(err)}, 400


@auth_bp.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("auth.welcome"))
    return render_template("homepage.html")


@auth_bp.route("/home")
def homepage():
    return render_template("homepage.html")


@auth_bp.route("/login")
def login():
    nextpage = request.args.get("next")
    if not nextpage:
        nextpage = url_for("auth.welcome")
    return render_template("login.html", next=nextpage)


@auth_bp.route("/register")
def register():
    nextpage = request.args.get("next")
    if not nextpage:
        nextpage = url_for("auth.welcome")
    return render_template("register.html", next=nextpage)


@auth_bp.route("/welcome")
@login_required
def welcome():
    return render_template("welcome.html", user=current_user)


@auth_bp.route("/users/<int:uid>")
def users(uid):
    user = find_user(uid)
    if user:
        return render_template("welcome.html", user=find_user(uid))
    return render_template("notfound.html", error="未能找到用户。"), 404


@auth_bp.route("/edit-profile")
@login_required
def edit_profile():
    return render_template("edit_profile.html")


@auth_bp.route("/avatars/<int:uid>")
def avatarfile(uid):
    user = find_user(uid)
    if not user or not user.avatar:
        return "", 404
    if not user.avlastmodified:
        user.avlastmodified = datetime.datetime.min
        db.session.commit()
    etag = hashlib.md5(user.avatar).hexdigest()
    if_none_match = request.headers.get("If-None-Match")
    if_modified_since = request.headers.get("If-Modified-Since")
    if if_none_match and if_none_match == etag:
        return "", 304
    if if_modified_since:
        try:
            client_time = datetime.datetime.strptime(
                if_modified_since, "%a, %d %b %Y %H:%M:%S GMT"
            )
            if client_time >= user.avlastmodified.replace(microsecond=0):
                return "", 304
        except ValueError:
            return "", 400
    response = make_response(user.avatar)
    response.headers["Content-Type"] = user.avmimetype or "image/jpeg"
    response.headers["ETag"] = etag
    response.headers["Last-Modified"] = user.avlastmodified.strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )
    response.headers["Cache-Control"] = "public, max-age=600"
    return response
