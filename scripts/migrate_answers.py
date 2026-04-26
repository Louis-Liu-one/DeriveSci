#!/usr/bin/env python3
"""
Simple migration script: normalize Prob.answer to nested format (list of subproblems).
Run with the project virtualenv activated, from project root:

    python3 scripts/migrate_answers.py

It will wrap old-format answers (a list of [context,answer] pairs) into a single subproblem list.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import app
from models import db, Prob

with app.app_context():
    probs = Prob.query.all()
    changed = 0
    for p in probs:
        if not p.answer:
            continue
        try:
            val = json.loads(p.answer)
        except Exception:
            print(f"Failed to parse Prob {p.probno} answer.")
            continue
        if isinstance(val, list) and val and all(isinstance(item, list) and len(item) == 2 for item in val):
            # old format -> wrap
            newval = [val]
            p.answer = json.dumps(newval)
            db.session.add(p)
            print(f"Normalized Prob {p.probno} answer from old format to new format.")
            changed += 1
    if changed:
        db.session.commit()
    print(f"Normalized {changed} Prob.answer entries.")
