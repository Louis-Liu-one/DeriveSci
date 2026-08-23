'''
Copyright (c) 2026 Zatursure  All rights reserved.
'''

import os
import json

from flask import Blueprint, current_app, render_template

helps_bp = Blueprint("helps", __name__, url_prefix="/helps")

helpdir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "templates", "helps")
jsonpath = os.path.join(helpdir, "helps-info.json")
if os.path.exists(jsonpath):
    with open(jsonpath, "r", encoding="utf-8") as fh:
        helps_info = json.load(fh)
else:
    helps_info = {}


@helps_bp.route("/")
def helplist():
    return render_template("helplist.html", helps_info=helps_info)


@helps_bp.route("/<howto>")
def helps(howto):
    help_info = helps_info.get(howto)
    if help_info is None:
        return render_template("notfound.html", error="未能找到帮助文档。"), 404
    return render_template("helps.html", help_info=help_info)