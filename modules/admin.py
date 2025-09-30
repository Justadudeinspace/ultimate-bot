"""Admin moderation commands: ban, kick, mute, unmute, warn, purge, setrules"""
import os, sqlite3
from aiogram import Router, F
from aiogram.types import Message, ChatPermissions
from db import get_conn

router = Router()

def is_admin_or_owner(message: Message):
    # Very small check: owner bypass
    owner = int(os.getenv('OWNER_ID', '0'))
    if message.from_user and message.from_user.id == owner:
        return True
    # if bot can't check chat admins here, allow commands only by chat admins in real use
    return message.from_user and message.from_user.id == owner  # stub: owner-only for safety

@router.message(F.text.startswith('/setrules'))
async def set_rules(m: Message):
    owner = int(os.getenv('OWNER_ID','0'))
    if not is_admin_or_owner(m):
        return await m.reply('Only owner can set rules in this starter.')
    text = m.text.removeprefix('/setrules').strip() or (m.reply_to_message.text if m.reply_to_message else None)
    if not text:
        return await m.reply('Usage: /setrules <text> (or reply with text)')
    conn = get_conn(); c = conn.cursor()
    c.execute('REPLACE INTO rules (chat_id, rules_text) VALUES (?,?)', (m.chat.id, text))
    conn.commit(); conn.close()
    await m.reply('Rules set for this chat.')

@router.message(F.text == '/rules')
async def show_rules(m: Message):
    conn = get_conn(); c = conn.cursor()
    c.execute('SELECT rules_text FROM rules WHERE chat_id=?', (m.chat.id,))
    row = c.fetchone(); conn.close()
    if not row:
        return await m.reply('No rules set for this chat. Owner can set with /setrules.')
    await m.reply(row[0])

@router.message(F.text.startswith('/ban'))
async def ban_user(m: Message):
    if not is_admin_or_owner(m):
        return await m.reply('Only owner can use this starter ban command.')
    target = None
    if m.reply_to_message:
        target = m.reply_to_message.from_user.id
    else:
        parts = m.text.split()
        if len(parts) >= 2 and parts[1].lstrip('@').isdigit():
            target = int(parts[1])
    if not target:
        return await m.reply('Usage: reply to a user with /ban or /ban <user_id>')
    try:
        await m.chat.ban(user_id=target)
        await m.reply('User banned.')
    except Exception as e:
        await m.reply(f'Failed to ban: {e}')

@router.message(F.text.startswith('/unban'))
async def unban_user(m: Message):
    if not is_admin_or_owner(m):
        return await m.reply('Only owner can use unban in this starter.')
    parts = m.text.split()
    if len(parts) < 2:
        return await m.reply('Usage: /unban <user_id>')
    target = int(parts[1])
    try:
        await m.chat.unban(user_id=target)
        await m.reply('User unbanned.')
    except Exception as e:
        await m.reply(f'Failed to unban: {e}')

@router.message(F.text.startswith('/kick'))
async def kick_user(m: Message):
    if not is_admin_or_owner(m):
        return await m.reply('Only owner can use kick in this starter.')
    if m.reply_to_message:
        target = m.reply_to_message.from_user.id
    else:
        return await m.reply('Reply to a user with /kick')
    try:
        await m.chat.kick(user_id=target)
        await m.reply('User kicked.')
    except Exception as e:
        await m.reply(f'Failed to kick: {e}')

@router.message(F.text.startswith('/mute'))
async def mute_user(m: Message):
    if not is_admin_or_owner(m):
        return await m.reply('Only owner can use mute in this starter.')
    if m.reply_to_message:
        target = m.reply_to_message.from_user.id
    else:
        return await m.reply('Reply to a user with /mute <minutes>')
    parts = m.text.split()
    minutes = 60
    if len(parts) >= 2 and parts[1].isdigit():
        minutes = int(parts[1])
    until = None
    try:
        # restrict sending messages
        perms = ChatPermissions(can_send_messages=False)
        await m.chat.restrict(user_id=target, permissions=perms)
        await m.reply(f'User muted for {minutes} minutes (manual unmute in starter).')
    except Exception as e:
        await m.reply(f'Failed to mute: {e}')

@router.message(F.text.startswith('/unmute'))
async def unmute_user(m: Message):
    if not is_admin_or_owner(m):
        return await m.reply('Only owner can use unmute in this starter.')
    if m.reply_to_message:
        target = m.reply_to_message.from_user.id
    else:
        return await m.reply('Reply to a user with /unmute')
    try:
        perms = ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
        await m.chat.restrict(user_id=target, permissions=perms)
        await m.reply('User unmuted.')
    except Exception as e:
        await m.reply(f'Failed to unmute: {e}')

@router.message(F.text.startswith('/warn'))
async def warn_user(m: Message):
    if not is_admin_or_owner(m):
        return await m.reply('Only owner can warn in this starter.')
    if not m.reply_to_message:
        return await m.reply('Reply to a user with /warn <reason>')
    reason = ' '.join(m.text.split()[1:]) or 'No reason provided'
    target = m.reply_to_message.from_user.id
    conn = get_conn(); c = conn.cursor()
    c.execute('INSERT INTO warnings (chat_id,user_id,reason) VALUES (?,?,?)', (m.chat.id, target, reason))
    conn.commit(); conn.close()
    await m.reply('User warned (logged).')

@router.message(F.text.startswith('/purge'))
async def purge_msgs(m: Message):
    if not is_admin_or_owner(m):
        return await m.reply('Only owner can purge in this starter.')
    parts = m.text.split()
    n = 10
    if len(parts) >= 2 and parts[1].isdigit():
        n = int(parts[1])
    # naive: delete last n messages by message id scanning (limited by bot rights)
    deleted = 0
    async for msg in m.chat.get_history(limit=n+1):
        try:
            await msg.delete()
            deleted += 1
        except Exception:
            pass
    await m.reply(f'Attempted to delete up to {n} messages; deleted {deleted}.')
