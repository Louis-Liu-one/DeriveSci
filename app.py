"""
Copyright (c) 2026 Louis Liu  All rights reserved.
Copyright (c) 2026 Zatursure  All rights reserved.
"""

import os

from dotenv import load_dotenv
from flask import Flask, request, render_template
from flask_moment import Moment

from models import db, init_app, auto_format_time, find_user
from anschecker import TPStatus
from blueprints import register_all

load_dotenv(override=True)
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
init_app(app)
moment = Moment(app)

register_all(app)


@app.route("/")
def home():
    from flask_login import current_user
    from flask import redirect, url_for

    if current_user.is_authenticated:
        return redirect(url_for("auth.welcome"))
    return render_template("homepage.html")


@app.errorhandler(404)
def page_not_found(error):
    if request.path.startswith("/api/"):
        return {"ok": False, "error": f"服务器出现问题：{error}"}, 404
    return render_template("notfound.html", error="未能找到页面。"), 404


app.jinja_env.add_extension("jinja2.ext.do")
app.add_template_global(find_user, "find_user")
app.add_template_global(auto_format_time, "auto_format_time")
app.add_template_global(TPStatus, "TPStatus")
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
