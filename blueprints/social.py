"""
Copyright (c) 2026 Louis Liu  All rights reserved.
Copyright (c) 2026 Zatursure  All rights reserved.

社交相关路由：
/social/chat                        聊天页面

/api/comment/post                  发布评论（接口）
/api/comment/delete                删除评论（接口）
/api/chat/update-lastvisit         更新聊天最后访问时间（接口）
/api/chat/send                     发送聊天消息（接口）
/api/chat/messages                 获取聊天消息（接口）
"""

import datetime

from flask import (
    Blueprint,
    request,
    jsonify,
    abort,
    render_template,
    render_template_string,
)
from flask_login import current_user, login_required
from flask_moment import moment as builtin_moment

from models import db, find_user, update_chatlastvisit, Comment, get_comment

social_bp = Blueprint("social", __name__, url_prefix="/social")


def register_social_api(app):

    @app.route("/api/comment/delete", methods=["POST"])
    def api_delete_comment():
        if not current_user.is_authenticated:
            return {"ok": False, "error": "用户未登录。"}, 401
        commentid = int(request.json.get("commentid"))
        comment = get_comment(commentid)
        if not comment:
            return {"ok": False, "error": "未找到评论，此条评论可能已被删除。"}, 404
        if not comment.editable_for(current_user):
            abort(403)
        db.session.delete(comment)
        db.session.commit()
        return {"ok": True}

    @app.route("/api/comment/post", methods=["POST"])
    def api_post_comment():
        if not current_user.is_authenticated:
            return {"ok": False, "error": "用户未登录。"}, 401
        data = request.json
        post_type = data.get("post_type")
        post_ident = data.get("post_ident")
        content = data.get("content")
        replyto_id = data.get("replyto_id")
        if not content:
            return {"ok": False, "error": "评论内容不能为空。"}, 400
        comment = Comment(
            user=current_user,
            content=content,
            post_type=post_type,
            post_ident=post_ident,
            replyto_id=replyto_id,
        )
        db.session.add(comment)
        db.session.commit()
        rendered_html = render_template_string(
            '{% from "includes/comment.html" import commentdiv with context %}'
            "{{ commentdiv(comment, toplevel=toplevel, "
            "secondlevel=secondlevel) }}",
            comment=comment,
            toplevel=not bool(replyto_id),
            secondlevel=bool(replyto_id)
            and comment.replyto
            and not comment.replyto.replyto_id,
            moment=builtin_moment,
        )
        return {"ok": True, "html": rendered_html, "is_reply": bool(replyto_id)}

    @app.route("/api/chat/update-lastvisit", methods=["POST"])
    def api_chat_update_lastvisit():
        try:
            receiver_uid = request.json.get("receiver_uid")
            sender_uid = request.json.get("sender_uid")
            if not receiver_uid or not sender_uid:
                return {"ok": False, "error": "未能找到用户。"}, 400
            update_chatlastvisit(receiver_uid, sender_uid)
            return {"ok": True}
        except BaseException as err:
            return {"ok": False, "error": str(err)}, 400

    @app.route("/api/chat/send", methods=["POST"])
    def api_chat_send():
        try:
            receiver_uid = request.json.get("receiver_uid")
            sender_uid = request.json.get("sender_uid")
            message = request.json.get("message")
            find_user(sender_uid).chat_to(receiver_uid, message)
            return {"ok": True}
        except BaseException as err:
            return {"ok": False, "error": str(err)}, 400

    @app.route("/api/chat/messages", methods=["POST"])
    def api_chat_messages():
        try:
            receiver_uid = int(request.json.get("receiver_uid"))
            lastmsgtime = request.json.get("lastmsgtime")
            return jsonify(
                find_user(receiver_uid).all_chats(
                    datetime.datetime.fromisoformat(lastmsgtime)
                    if lastmsgtime
                    else None
                )
            )
        except BaseException:
            return {}, 400


@social_bp.route("/chat")
@login_required
def chat():
    view_comments = request.args.get("view_comments", "False") == "True"
    if view_comments:
        return render_template("chat.html", view_comments=True)
    activeuid = request.args.get("activeuid")
    return render_template("chat.html", activeuser=find_user(activeuid))
