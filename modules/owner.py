"""Owner-only operations: stats, logs tail (stub), backup/export stubs"""
import os, shutil, sqlite3, time
from aiogram import Router, F
from db import get_conn, DB_PATH, MEDIA_DIR, ensure_media_dir

router = Router()

def owner_check(m):
    return m.from_user and m.from_user.id == int(os.getenv('OWNER_ID', '0'))

@router.message(F.text == '/stats')
async def stats(m):
    if not owner_check(m):
        return await m.reply('Owner-only.')
    # small stats stub
    db_size = os.path.getsize(os.getenv('DATABASE','./data/ultimate_bot.sqlite')) if os.path.exists(os.getenv('DATABASE','./data/ultimate_bot.sqlite')) else 0
    media_count = 0
    try:
        conn = get_conn(); c = conn.cursor(); c.execute('SELECT COUNT(*) FROM media'); media_count = c.fetchone()[0]; conn.close()
    except Exception:
        media_count = 0
    await m.reply(f'Stats:\nDB size: {db_size} bytes\nMedia items: {media_count}')

@router.message(F.text.startswith('/logs'))
async def logs(m):
    if not owner_check(m):
        return await m.reply('Owner-only.')
    # stub: show last lines of a simple logfile if exists
    lf = './data/ultimate-bot.log'
    if not os.path.exists(lf):
        return await m.reply('No log file found (starter).')
    tail = '\n'.join(open(lf,'r').read().splitlines()[-50:])
    await m.reply(f'Last log lines:\n{tail}')

@router.message(F.text == '/backup')
async def backup(m):
    if not owner_check(m):
        return await m.reply('Owner-only.')
    # create a simple zip of DB + media manifest
    import zipfile, io
    zipper = './data/backup_{}.zip'.format(int(time.time()))
    with zipfile.ZipFile(zipper, 'w') as zf:
        if os.path.exists(os.getenv('DATABASE','./data/ultimate_bot.sqlite')):
            zf.write(os.getenv('DATABASE','./data/ultimate_bot.sqlite'))
    await m.reply('Backup created: ' + zipper)
