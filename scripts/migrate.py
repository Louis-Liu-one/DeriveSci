#!/usr/bin/env python3
import os
import sqlite3
import sys


DB_PATH = os.environ.get('MATHPROBS_DB_PATH', 'instance/database.sqlite3')


def main():
    if not os.path.exists(DB_PATH):
        print(f'数据库文件不存在: {DB_PATH}')
        return 1

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='images'")
    if cur.fetchone() is None:
        print('images 表不存在，跳过迁移。')
        conn.close()
        return 0

    columns = [col['name'] for col in cur.execute('PRAGMA table_info(images)')]
    if 'post_type' in columns:
        print('images 表已经是新结构，跳过迁移。')
        conn.close()
        return 0

    print('开始迁移 images 表...')
    cur.execute('ALTER TABLE images RENAME TO images_old')
    cur.execute('''
        CREATE TABLE images (
            post_type INTEGER NOT NULL,
            post_ident TEXT NOT NULL,
            name VARCHAR(64) NOT NULL,
            uid INTEGER,
            size INTEGER,
            mimetype VARCHAR(64),
            data BLOB,
            PRIMARY KEY (post_type, post_ident, name),
            FOREIGN KEY(uid) REFERENCES users(uid)
        )
    ''')
    cur.execute('''
        INSERT INTO images (post_type, post_ident, name, uid, size, mimetype, data)
        SELECT 0, probno, name, uid, size, mimetype, data FROM images_old
    ''')
    cur.execute('DROP TABLE images_old')
    conn.commit()
    print('迁移完成。')
    conn.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
