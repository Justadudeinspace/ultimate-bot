"""Tiny SQLite helpers for starter repo"""
import os, sqlite3
from pathlib import Path

DB_PATH = os.getenv('DATABASE', './data/ultimate_bot.sqlite')
MEDIA_DIR = os.getenv('MEDIA_DIR', './data/media')

def init_db():
    os.makedirs(os.path.dirname(DB_PATH) or '.', exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # users, chats, warnings, media, guardians, rules
    c.execute('''CREATE TABLE IF NOT EXISTS warnings (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, user_id INTEGER, reason TEXT, count INTEGER DEFAULT 1, ts DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS media (id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER, title TEXT, filename TEXT, telegram_file_id TEXT, ts DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS guardians (id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER, tg_id INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS rules (chat_id INTEGER PRIMARY KEY, rules_text TEXT)''')
    conn.commit()
    conn.close()

def get_conn():
    return sqlite3.connect(DB_PATH)

def ensure_media_dir():
    os.makedirs(MEDIA_DIR, exist_ok=True)
