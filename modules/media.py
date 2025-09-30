"""Media library: upload/find/send — user-owned media only (stores uploads in MEDIA_DIR)"""
import os, tempfile, sqlite3, shutil
from pathlib import Path
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from db import get_conn, MEDIA_DIR

router = Router()

@router.message(F.content_type.in_({'audio','document'}) & F.text.startswith('/upload'))
async def upload_media(m: Message):
    # usage: attach audio and send message '/upload title - artist'
    file = m.audio or m.document
    if not file:
        return await m.reply('Attach an audio file (mp3/m4a) and include /upload <title> in the same message.')
    meta = m.text.removeprefix('/upload').strip() or 'Untitled'
    os.makedirs(MEDIA_DIR, exist_ok=True)
    # download file
    path = Path(MEDIA_DIR) / f"{file.file_unique_id}_{file.file_name or 'upload'}"
    await file.download(destination=path)
    # store DB row
    conn = get_conn(); c = conn.cursor()
    c.execute('INSERT INTO media (owner_id,title,filename,telegram_file_id) VALUES (?,?,?,?)', (m.from_user.id, meta, str(path), None))
    conn.commit(); conn.close()
    await m.reply('File stored in library. Use /find <query> to search.')

@router.message(F.text.startswith('/find'))
async def find_media(m: Message):
    q = m.text.removeprefix('/find').strip()
    if not q:
        return await m.reply('Usage: /find <query> (search title)')
    conn = get_conn(); c = conn.cursor()
    c.execute('SELECT id, title, filename FROM media WHERE title LIKE ? ORDER BY ts DESC LIMIT 10', (f'%{q}%',))
    rows = c.fetchall(); conn.close()
    if not rows:
        return await m.reply('No results. Try uploading or a different query.')
    text = '\n'.join([f"{r[0]}) {r[1]}" for r in rows])
    # store last search per chat in a temp file
    (Path(MEDIA_DIR)/f'last_search_{m.chat.id}.txt').write_text('\n'.join([str(r[0]) for r in rows]))
    await m.reply(f'Results:\n{text}\nUse /send <id> to send an item.')

@router.message(F.text.startswith('/send'))
async def send_media(m: Message):
    parts = m.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        return await m.reply('Usage: /send <media_id> (from /find)')
    mid = int(parts[1])
    conn = get_conn(); c = conn.cursor()
    c.execute('SELECT filename FROM media WHERE id=?', (mid,))
    row = c.fetchone(); conn.close()
    if not row:
        return await m.reply('Media id not found.')
    path = row[0]
    if not os.path.exists(path):
        return await m.reply('Stored file missing.')
    await m.reply_audio(audio=FSInputFile(path), caption=f'Shared media id={mid}')
