"""
Copyright (c) 2026 Louis Liu  All rights reserved.
Copyright (c) 2026 Zatursure  All rights reserved.

题目相关路由：
/probs/upload                           上传题目
/probs/collections/                     题目列表
/probs/collections/<probno>             查看题目
/probs/collections/<probno>/edit        编辑题目
/probs/collections/<probno>/submit      提交题目答案

/api/prob/search-content      搜索题目内容（接口）
/api/prob/upload              上传题目（接口）
/api/prob/edit                编辑题目（接口）
/api/prob/review              审核题目（接口）
/api/prob/review-comment      保存题目审核意见（接口）
/api/prob/set-official        设置题目为官方题目（接口）
/api/prob/delete              删除题目（接口）

题解相关路由：
/probs/collections/<probno>/upload-solution                   上传题解
/probs/collections/<probno>/solutions/<int:solno>             查看题解
/probs/collections/<probno>/solutions/<int:solno>/edit        编辑题解

/api/solution/upload           上传题解（接口）
/api/solution/edit             编辑题解（接口）
/api/solution/delete           删除题解（接口）

标签相关路由：
/probs/tags/                       标签列表
/probs/tags/<tagtitle>             查看标签下的题目列表

/api/tag/rename               重命名标签（接口）
"""

import json
import random

from flask import Blueprint, request, jsonify, abort, url_for, redirect, render_template
from flask_login import current_user, login_required

from models import db, Prob, get_prob, add_prob, get_solution, add_solution
from models import Tag, get_tag, add2tags, clear_comments, add_images
from anschecker import latex

probs_bp = Blueprint("probs", __name__, url_prefix="/probs")


def register_probs_api(app):

    @app.route("/api/tag/rename", methods=["POST"])
    def api_rename_tag():
        if not current_user.is_authenticated:
            return {"ok": False, "error": "用户未登录。"}, 401
        if not current_user.isadmin:
            abort(403)  # 无编辑标签的权限
        old_title = request.json.get("old_title")
        new_title = request.json.get("new_title")
        tag = get_tag(old_title)
        if not tag:
            return {"ok": False, "error": "未能找到标签。"}, 404
        status, result = tag.rename(new_title)
        if not status:
            return {"ok": False, "error": str(result)}, 400
        return {"ok": True, "url": result.url()}

    @app.route("/api/prob/search-content", methods=["POST"])
    def api_search_probs_content():
        data = request.get_json() or {}
        statement = data.get("statement", "")
        reviewmode = data.get("reviewmode") or request.args.get("reviewmode") == "True"
        oftag = data.get("oftag") or False
        tagtitle = data.get("tagtitle") or None
        if not statement:
            return jsonify({"results": []})
        q = Prob.query
        if oftag and tagtitle:
            q = q.filter(Prob.tags.any(Tag.tagtitle == tagtitle))
        if not reviewmode:
            q = q.filter(Prob.review_status == 1)
        q = q.filter(Prob.statement.like(f"%{statement}%")).order_by(Prob.probno.asc())
        probs_list = list(q)
        return jsonify({"results": [p.probno for p in probs_list]})

    @app.route("/api/prob/upload", methods=["POST"])
    def api_upload_prob():
        if not current_user.is_authenticated:
            return {"ok": False, "error": "用户未登录。"}, 401
        probno = request.form.get("probno")
        probtitle = request.form.get("probtitle")
        tags = json.loads(request.form.get("tags", "[]"))
        statement = request.form.get("statement")
        answers = request.form.get("answers")
        imgfiles = request.files.getlist("imgfiles")
        isofficial = current_user.isadmin and request.form.get("isofficial") == "on"
        review_status = 1 if current_user.isadmin else -1
        status, prob = add_prob(
            probno=probno,
            probtitle=probtitle,
            statement=statement,
            answer=answers,
            source=current_user,
            review_status=review_status,
            isofficial=isofficial,
        )
        if not status:
            return {"ok": False, "error": str(prob)}, 400
        error = add_images(0, prob.probno, imgfiles)
        if error is not None:
            return {"ok": False, "error": str(error)}, 400
        add2tags(tags, prob)
        return {"ok": True, "url": prob.url()}

    @app.route("/api/prob/edit", methods=["POST"])
    def api_edit_prob():
        if not current_user.is_authenticated:
            return {"ok": False, "error": "用户未登录。"}, 401
        probno = request.form.get("probno")
        prob = get_prob(probno)
        if not prob:
            return {"ok": False, "error": "未能找到题目。"}, 404
        if not prob.editable_for(current_user):
            abort(403)
        probtitle = request.form.get("probtitle")
        tags = json.loads(request.form.get("tags", "[]"))
        statement = request.form.get("statement")
        answers = request.form.get("answers")
        imgfiles = request.files.getlist("imgfiles")
        error = add_images(0, prob.probno, imgfiles)
        if error is not None:
            return {"ok": False, "error": str(error)}, 400
        prob.edit(probtitle, tags, statement, answers)
        return {"ok": True, "url": prob.url()}

    @app.route("/api/prob/review", methods=["POST"])
    def api_review_prob():
        if not current_user.is_authenticated:
            return {"ok": False, "error": "用户未登录。"}, 401
        if not current_user.isadmin:
            abort(403)
        probno = request.json.get("probno")
        accept = bool(request.json.get("accept"))
        prob = get_prob(probno)
        if not prob:
            return {"ok": False, "error": "未能找到题目。"}, 404
        prob.review_status = 1 if accept else 0
        review_comment = request.json.get("review_comment")
        if review_comment is not None:
            prob.review_comment = review_comment
        db.session.commit()
        return {
            "ok": True,
            "accept": accept,
            "url": prob.url() if accept else url_for("probs.problist"),
        }

    @app.route("/api/prob/review-comment", methods=["POST"])
    def api_save_review_comment():
        if not current_user.is_authenticated:
            return {"ok": False, "error": "用户未登录。"}, 401
        if not current_user.isadmin:
            abort(403)
        probno = request.json.get("probno")
        comment = request.json.get("review_comment")
        prob = get_prob(probno)
        if not prob:
            return {"ok": False, "error": "未能找到题目。"}, 404
        prob.review_comment = comment
        db.session.commit()
        return {"ok": True}

    @app.route("/api/prob/set-official", methods=["POST"])
    def api_set_official_prob():
        if not current_user.is_authenticated:
            return {"ok": False, "error": "用户未登录。"}, 401
        if not current_user.isadmin:
            abort(403)
        probno = request.json.get("probno")
        prob = get_prob(probno)
        if not prob:
            return {"ok": False, "error": "未能找到题目。"}, 404
        prob.isofficial = not prob.isofficial
        db.session.commit()
        return {"ok": True, "isofficial": prob.isofficial}

    @app.route("/api/prob/delete", methods=["POST"])
    def api_delete_prob():
        if not current_user.is_authenticated:
            return {"ok": False, "error": "用户未登录。"}, 401
        probno = request.json.get("probno")
        prob = get_prob(probno)
        if not prob or not prob.viewable_for(current_user):
            return {"ok": False, "error": "未能找到题目。"}, 404
        if not prob.editable_for(current_user):
            abort(403)
        prob.tags.clear()
        clear_comments(prob)
        db.session.delete(prob)
        db.session.commit()
        return {"ok": True, "url": url_for("probs.problist")}

    @app.route("/api/solution/upload", methods=["POST"])
    def api_upload_solution():
        if not current_user.is_authenticated:
            return {"ok": False, "error": "用户未登录。"}, 401
        probno = request.form.get("probno")
        prob = get_prob(probno)
        if not prob:
            return {"ok": False, "error": "未能找到题目。"}, 404
        soltitle = request.form.get("soltitle")
        content = request.form.get("solution")
        imgfiles = request.files.getlist("imgfiles")
        status, solution = add_solution(probno, soltitle, content)
        if not status:
            return {"ok": False, "error": str(solution)}, 400
        error = add_images(1, solution.get_post_ident(), imgfiles)
        if error is not None:
            return {"ok": False, "error": str(error)}, 400
        return {"ok": True, "url": solution.url()}

    @app.route("/api/solution/edit", methods=["POST"])
    def api_edit_solution():
        if not current_user.is_authenticated:
            return {"ok": False, "error": "用户未登录。"}, 401
        probno = request.form.get("probno")
        solno = int(request.form.get("solno"))
        solution = get_solution(probno, solno)
        if not solution or not solution.viewable_for(current_user):
            return {"ok": False, "error": "未能找到题解。"}, 404
        if not solution.editable_for(current_user):
            abort(403)
        soltitle = request.form.get("soltitle")
        content = request.form.get("solution")
        imgfiles = request.files.getlist("imgfiles")
        error = add_images(1, solution.get_post_ident(), imgfiles)
        if error is not None:
            return {"ok": False, "error": str(error)}, 400
        solution.edit(soltitle, content)
        return {"ok": True, "url": solution.url()}

    @app.route("/api/solution/delete", methods=["POST"])
    def api_delete_solution():
        if not current_user.is_authenticated:
            return {"ok": False, "error": "用户未登录。"}, 401
        probno = request.json.get("probno")
        solno = int(request.json.get("solno"))
        solution = get_solution(probno, solno)
        prob_url = solution.prob.url()
        if not solution or not solution.viewable_for(current_user):
            return {"ok": False, "error": "未能找到题解。"}, 404
        if not solution.editable_for(current_user):
            abort(403)
        clear_comments(solution)
        db.session.delete(solution)
        db.session.commit()
        return {"ok": True, "url": prob_url}


@probs_bp.route("/collections/")
def problist():
    reviewmode = request.args.get("reviewmode") == "True"
    if reviewmode and not (current_user.is_authenticated and current_user.isadmin):
        return redirect(url_for("probs.problist"))
    if reviewmode:
        all_query = Prob.query.order_by(Prob.probno.asc())
    else:
        all_query = Prob.query.filter(Prob.review_status == 1).order_by(
            Prob.probno.asc()
        )
    probs_data = [p.probno for p in all_query]
    probs = list(all_query)
    return render_template(
        "problist.html",
        reviewmode=reviewmode,
        probs=probs,
        probs_data=probs_data,
        form={},
    )


@probs_bp.route("/tags/")
def taglist():
    return render_template("taglist.html", tags=Tag.query.all())


@probs_bp.route("/tags/<tagtitle>")
def problistoftag(tagtitle):
    base_query = Prob.query.filter(Prob.tags.any(Tag.tagtitle == tagtitle))
    if not current_user.is_authenticated or not current_user.isadmin:
        base_query = base_query.filter(Prob.review_status == 1)
    all_query = base_query.order_by(Prob.probno.asc())
    probs_data = [p.probno for p in all_query]
    probs = list(all_query)
    return render_template(
        "problist.html",
        tagtitle=tagtitle,
        oftag=True,
        form={},
        probs=probs,
        probs_data=probs_data,
        query=None,
    )


@probs_bp.route("/collections/<probno>")
def probs(probno):
    prob = get_prob(probno)
    if prob and prob.viewable_for(current_user):
        return render_template("prob.html", prob=prob)
    return render_template("notfound.html", error="未能找到题目。"), 404


@probs_bp.route("/collections/<probno>/submit", methods=["POST"])
@login_required
def submit(probno):
    answers = [a.strip() for a in request.form.getlist("answertext")]
    prob = get_prob(probno)
    if not prob or not prob.viewable_for(current_user):
        return render_template("notfound.html", error="未能找到题目。"), 404
    answer_payload = answers if len(answers) > 1 else (answers[0] if answers else "")
    answer_eval, testpoints, submission = prob.add_submission(
        current_user, answer_payload
    )
    if isinstance(answer_eval, list):
        answer_latex = [latex(a) if a is not None else None for a in answer_eval]
    else:
        answer_latex = latex(answer_eval) if answer_eval is not None else None
    submission_answer_parsed = None
    if submission and submission.answer:
        try:
            val = json.loads(submission.answer)
            if isinstance(val, list):
                submission_answer_parsed = val
            else:
                submission_answer_parsed = [str(val)]
        except Exception:
            submission_answer_parsed = [submission.answer]
    return render_template(
        "submit.html",
        answer_latex=answer_latex,
        prob=prob,
        submission=submission,
        testpoints=testpoints,
        submission_answer_parsed=submission_answer_parsed,
    )


@probs_bp.route("/collections/<probno>/solutions/<int:solno>")
def solutions(probno, solno):
    solution = get_solution(probno, solno)
    if not solution or not solution.viewable_for(current_user):
        return render_template("notfound.html", error="未能找到题解。"), 404
    prob = solution.prob
    solutions = prob.solutions.copy()
    solutions.remove(solution)
    suggested = random.sample(solutions, min(len(solutions), 3))
    return render_template(
        "solution.html", prob=prob, solution=solution, suggested=suggested
    )


@probs_bp.route("/collections/<probno>/edit")
@login_required
def edit_prob(probno):
    prob = get_prob(probno)
    if not prob:
        return render_template("notfound.html", error="未能找到题目。"), 404
    if not prob.editable_for(current_user):
        return redirect(prob.url())
    return render_template("upload_prob.html", editmode=True, prob=prob)


@probs_bp.route("/collections/<probno>/solutions/<int:solno>/edit")
@login_required
def edit_solution(probno, solno):
    solution = get_solution(probno, solno)
    if not solution or not solution.viewable_for(current_user):
        return render_template("notfound.html", error="未能找到题解。"), 404
    if current_user != solution.user and not current_user.isadmin:
        return redirect(solution.url())
    return render_template(
        "upload_solution.html", editmode=True, prob=solution.prob, solution=solution
    )


@probs_bp.route("/upload")
@login_required
def upload_prob():
    return render_template("upload_prob.html")


@probs_bp.route("/collections/<probno>/upload-solution")
@login_required
def upload_solution(probno):
    prob = get_prob(probno)
    if not prob:
        return render_template("notfound.html", error="未能找到题目。"), 404
    return render_template("upload_solution.html", prob=prob)
