#!/usr/bin/env python3
"""将旧 answers 格式迁移为新的 subproblem 对象格式。

用法: 在 virtualenv 激活后运行:
    python3 scripts/migrate_answers_to_subprobs.py

该脚本会遍历所有 Prob，若其 answer 字段是 JSON 列表且列表元素为 list（legacy tps 列表），
则将其替换为 [{'label': '', 'tps': <原列表>} ...] 并保存到数据库。
"""
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
from app import app, db
from models import Prob


def migrate():
    with app.app_context():
        probs = Prob.query.all()
        changed = 0
        for p in probs:
            if not p.answer:
                print(f"Prob {p.probno} has empty answer, skipping.")
                continue
            try:
                val = json.loads(p.answer)
            except Exception:
                print(f"Prob {p.probno} has invalid JSON answer, skipping.")
                continue
            if not isinstance(val, list):
                print(f"Prob {p.probno} has non-list answer, skipping.")
                continue
            needs = False
            newlist = []
            for item in val:
                if isinstance(item, list):
                    needs = True
                    newlist.append({'label': '', 'tps': item})
                elif isinstance(item, dict):
                    newlist.append(item)
                else:
                    print(f"Prob {p.probno} has unexpected item type in answer, skipping.")
                    continue
            if needs:
                p.answer = json.dumps(newlist, ensure_ascii=False)
                db.session.add(p)
                changed += 1
            print(f"Checked Prob {p.probno}, {'updated' if needs else 'no change'}.")
        if changed:
            db.session.commit()
        print(f"Migration complete. {changed} problems updated.")


if __name__ == '__main__':
    migrate()
