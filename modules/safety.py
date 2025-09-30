"""Safety / Bodyguard features: SOS, trust list, silent alarm, escort (starter)"""
import os, sqlite3, uuid, time
from aiogram import Router, F
from aiogram.types import Message
from db import get_conn

router = Router()

def is_owner(user_id: int):
    return user_id == int(os.getenv('OWNER_ID', '0'))

@router.message(F.text.startswith('/trust'))
async def trust_cmd(m: Message):
    # /trust add <tg_id>  OR /trust list
    parts = m.text.split()
    if len(parts) >= 2 and parts[1] == 'add' and len(parts) == 3 and parts[2].isdigit():
        tg = int(parts[2])
        conn = get_conn(); c = conn.cursor()
        c.execute('INSERT INTO guardians (owner_id,tg_id) VALUES (?,?)', (m.from_user.id, tg))
        conn.commit(); conn.close()
        return await m.reply('Guardian added.')
    if len(parts) >= 2 and parts[1] == 'list':
        conn = get_conn(); c = conn.cursor()
        c.execute('SELECT tg_id FROM guardians WHERE owner_id=?', (m.from_user.id,))
        rows = c.fetchall(); conn.close()
        if not rows: return await m.reply('No guardians configured.')
        await m.reply('Guardians:\n' + '\n'.join([str(r[0]) for r in rows]))
    return await m.reply('Usage: /trust add <tg_id> | /trust list')

@router.message(F.text.startswith('/sos'))
async def sos_cmd(m: Message):
    # Minimal SOS: notify guardians with text + optional replied location
    reason = m.text.removeprefix('/sos').strip() or 'SOS'
    conn = get_conn(); c = conn.cursor()
    c.execute('SELECT tg_id FROM guardians WHERE owner_id=?', (m.from_user.id,))
    rows = c.fetchall()
    c.execute('INSERT INTO safety_events (id,owner_id,reason,ts) VALUES (?,?,?,CURRENT_TIMESTAMP)') if False else None
    if not rows:
        return await m.reply('No guardians set. Use /trust add <tg_id> to add them.')
    for r in rows:
        try:
            await m.bot.send_message(r[0], f'🚨 SOS from @{m.from_user.username or m.from_user.id}: {reason}')
            # forward location if present
            if m.reply_to_message and m.reply_to_message.location:
                await m.bot.send_location(r[0], latitude=m.reply_to_message.location.latitude, longitude=m.reply_to_message.location.longitude)
        except Exception:
            pass
    await m.reply('SOS sent to guardians (starter).')

@router.message(F.text.startswith('/silent'))
async def silent_sos(m: Message):
    # silent: same as sos but don't post publicly (just ack)
    reason = m.text.removeprefix('/silent').strip() or 'Silent SOS'
    conn = get_conn(); c = conn.cursor()
    c.execute('SELECT tg_id FROM guardians WHERE owner_id=?', (m.from_user.id,))
    rows = c.fetchall()
    for r in rows:
        try:
            await m.bot.send_message(r[0], f'(Silent) 🚨 SOS from @{m.from_user.username or m.from_user.id}: {reason}')
            if m.reply_to_message and m.reply_to_message.location:
                await m.bot.send_location(r[0], latitude=m.reply_to_message.location.latitude, longitude=m.reply_to_message.location.longitude)
        except Exception:
            pass
    await m.reply('Silent SOS dispatched to guardians (starter).')
