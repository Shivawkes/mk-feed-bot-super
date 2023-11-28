""" Create Module """
from datetime import datetime
import sqlite3
import time
import os
from misskey import Misskey
from dotenv import load_dotenv

load_dotenv()

def publish_note():
    """ Takes the latest published news and posts a note """
    local_only = os.getenv('LOCAL', 'False').lower() in ('true', '1', 't', 'on', 'ok')

    db = sqlite3.connect('feed-bot.sqlite')
    c = db.cursor()
    mk = Misskey(os.getenv('HOST'), i=os.getenv('APIKEY'))

    c.execute('''
        SELECT * FROM news WHERE noted = 0 ORDER BY publishedAt DESC LIMIT 1
    ''')
    d = c.fetchone()

    if d is not None:
        text = d[1] + "\n<b>" + d[4] + "</b>\n" + d[5] + "\n\n" + d[3]
        time.sleep(2)
        api = mk.notes_create(
            text=text,
            visibility=os.getenv('VISIBILITY', 'public'),
            local_only=local_only,
        )
        n_id = api['createdNote']['id']
        n_at = int(datetime.strptime(
            api['createdNote']['createdAt'], '%Y-%m-%dT%H:%M:%S.%fZ'
        ).timestamp())

        c.execute('''
            UPDATE news SET noted = 1, noteId = ?, notedAt = ? WHERE id = ?
        ''', (n_id, n_at, d[0]))
        db.commit()
    db.close()
