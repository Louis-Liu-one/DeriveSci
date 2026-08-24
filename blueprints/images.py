'''
Copyright (c) 2026 Louis Liu  All rights reserved.
Copyright (c) 2026 Zatursure  All rights reserved.

图片操作相关路由
'''

import hashlib

from flask import Blueprint, request, abort, url_for, render_template, make_response
from flask_login import current_user

from models import db, get_post, get_image, get_images_for_post, Image

images_bp = Blueprint("images", __name__, url_prefix="/images")


def register_images_api(app):

    @app.route("/api/image/reupload", methods=["POST"])
    def api_image_reupload():
        if not current_user.is_authenticated:
            return {"ok": False, "error": "用户未登录。"}, 401
        post_type = request.form.get("post_type")
        post_ident = request.form.get("post_ident")
        name = request.form.get("name")
        imgfile = request.files.get("imgfile")
        if not post_type or not post_ident or not name or not imgfile:
            return {"ok": False, "error": "参数不足。"}, 400
        image = get_image(post_type, post_ident, name)
        if not image:
            return {"ok": False, "error": "未能找到图片。"}, 404
        if not current_user == image.uploader and not current_user.isadmin:
            abort(403)
        data = imgfile.read()
        if not data:
            return {"ok": False, "error": "上传文件为空。"}, 400
        image.data = data
        image.size = len(data)
        image.mimetype = imgfile.mimetype or image.mimetype
        db.session.commit()
        return {"ok": True}

    @app.route("/api/image/rename", methods=["POST"])
    def api_image_rename():
        if not current_user.is_authenticated:
            return {"ok": False, "error": "用户未登录。"}, 401
        post_type = request.json.get("post_type")
        post_ident = request.json.get("post_ident")
        oldname = request.json.get("oldname")
        newname = request.json.get("newname")
        if not post_type or not post_ident or not oldname or not newname:
            return {"ok": False, "error": "参数不足。"}, 400
        image = get_image(post_type, post_ident, oldname)
        if not image:
            return {"ok": False, "error": "未能找到图片。"}, 404
        if not current_user == image.uploader and not current_user.isadmin:
            abort(403)
        exists = get_image(post_type, post_ident, newname)
        if exists:
            return {"ok": False, "error": "目标文件名已存在。"}, 400
        newimg = Image(
            post_type=image.post_type, post_ident=image.post_ident,
            name=newname, uid=image.uid, size=image.size,
            mimetype=image.mimetype, data=image.data)
        db.session.add(newimg)
        db.session.delete(image)
        db.session.commit()
        return {"ok": True, "newurl": url_for(
            "images.image_preview", post_type=post_type, post_ident=post_ident,
            imagename=newname)}

    @app.route("/api/image/delete", methods=["POST"])
    def api_image_delete():
        if not current_user.is_authenticated:
            return {"ok": False, "error": "用户未登录。"}, 401
        post_type = request.json.get("post_type")
        post_ident = request.json.get("post_ident")
        name = request.json.get("name")
        if not post_type or not post_ident or not name:
            return {"ok": False, "error": "参数不足。"}, 400
        image = get_image(post_type, post_ident, name)
        if not image:
            return {"ok": False, "error": "未能找到图片。"}, 404
        if not current_user == image.uploader and not current_user.isadmin:
            abort(403)
        db.session.delete(image)
        db.session.commit()
        return {"ok": True, "url": url_for(
            "images.images_list", post_type=post_type, post_ident=post_ident)}


@images_bp.route("/<int:post_type>/<post_ident>/")
def images_list(post_type, post_ident):
    post = get_post(post_type, post_ident)
    if not post or not post.viewable_for(current_user):
        return render_template("notfound.html", error="未能找到内容。"), 404
    images = get_images_for_post(post_type, post_ident)
    return render_template(
        "images.html", target=post, post_type=post_type,
        post_ident=post_ident, images=images)


@images_bp.route("/<int:post_type>/<post_ident>/<imagename>/view")
def image_preview(post_type, post_ident, imagename):
    post = get_post(post_type, post_ident)
    if not post or not post.viewable_for(current_user):
        return render_template("notfound.html", error="未能找到内容。"), 404
    image = get_image(post_type, post_ident, imagename)
    if not image:
        return render_template("notfound.html", error="未能找到图片。"), 404
    editable = current_user.is_authenticated and (
        hasattr(image, "uid") and current_user.uid == image.uid
        or current_user.isadmin)
    return render_template(
        "image.html", target=post, post_type=post_type,
        post_ident=post_ident, image=image, editable=editable)


@images_bp.route("/<int:post_type>/<post_ident>/<imagename>")
def imagefile(post_type, post_ident, imagename):
    image = get_image(post_type, post_ident, imagename)
    if not image:
        abort(404)
    etag = hashlib.md5(image.data).hexdigest()
    if_none_match = request.headers.get("If-None-Match")
    if if_none_match and if_none_match == etag:
        return "", 304
    response = make_response(image.data)
    response.headers["Content-Type"] = image.mimetype
    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "public, max-age=600"
    return response