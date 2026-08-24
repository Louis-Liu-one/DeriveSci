"""
Copyright (c) 2026 Louis Liu  All rights reserved.
Copyright (c) 2026 Zatursure  All rights reserved.

专栏相关路由：
/articles/upload                上传专栏
/articles/<int:article_id>      查看专栏
/articles/<int:article_id>/edit 编辑专栏

/api/article/upload             上传专栏（接口）
/api/article/edit               编辑专栏（接口）
/api/article/delete             删除专栏（接口）
"""

from flask import Blueprint, request, abort, url_for, redirect, render_template
from flask_login import current_user, login_required

from models import db, get_article, add_article, clear_comments, add_images

articles_bp = Blueprint("articles", __name__, url_prefix="/articles")


def register_articles_api(app):

    @app.route("/api/article/upload", methods=["POST"])
    def api_upload_article():
        if not current_user.is_authenticated:
            return {"ok": False, "error": "用户未登录。"}, 401
        title = request.form.get("articletitle")
        content = request.form.get("article")
        imgfiles = request.files.getlist("imgfiles")
        status, article = add_article(title, content)
        error = add_images(3, article.get_post_ident(), imgfiles)
        if error is not None:
            return {"ok": False, "error": str(error)}, 400
        if not status:
            return {"ok": False, "error": str(article)}, 400
        return {"ok": True, "url": article.url()}

    @app.route("/api/article/edit", methods=["POST"])
    def api_edit_article():
        if not current_user.is_authenticated:
            return {"ok": False, "error": "用户未登录。"}, 401
        article_id = int(request.form.get("article_id"))
        article = get_article(article_id)
        if not article or not article.viewable_for(current_user):
            return {"ok": False, "error": "未能找到专栏。"}, 404
        if not article.editable_for(current_user):
            abort(403)
        title = request.form.get("articletitle")
        content = request.form.get("article")
        imgfiles = request.files.getlist("imgfiles")
        error = add_images(3, article.get_post_ident(), imgfiles)
        if error is not None:
            return {"ok": False, "error": str(error)}, 400
        article.edit(title, content)
        return {"ok": True, "url": article.url()}

    @app.route("/api/article/delete", methods=["POST"])
    def api_delete_article():
        if not current_user.is_authenticated:
            return {"ok": False, "error": "用户未登录。"}, 401
        article_id = int(request.json.get("article_id"))
        article = get_article(article_id)
        if not article or not article.viewable_for(current_user):
            return {"ok": False, "error": "未能找到专栏。"}, 404
        if not article.editable_for(current_user):
            abort(403)
        clear_comments(article)
        db.session.delete(article)
        db.session.commit()
        return {"ok": True, "url": url_for("auth.homepage")}


@articles_bp.route("/upload")
@login_required
def upload_article():
    return render_template("upload_article.html", editmode=False)


@articles_bp.route("/<int:article_id>")
def article(article_id):
    article = get_article(article_id)
    if not article or not article.viewable_for(current_user):
        return render_template("notfound.html", error="未能找到专栏。"), 404
    return render_template("article.html", article=article)


@articles_bp.route("/<int:article_id>/edit")
@login_required
def edit_article(article_id):
    article = get_article(article_id)
    if not article or not article.viewable_for(current_user):
        return render_template("notfound.html", error="未能找到专栏。"), 404
    if current_user != article.user and not current_user.isadmin:
        return redirect(article.url())
    return render_template("upload_article.html", editmode=True, article=article)
