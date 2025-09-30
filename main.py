#!/usr/bin/env python3
"""Ultimate Bot — entrypoint (aiogram v3 style)"""
import os, asyncio, logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from modules import admin, media, safety, owner
from db import init_db, ensure_media_dir

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise RuntimeError('BOT_TOKEN missing in env')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ultimate-bot')

async def on_startup(bot: Bot):
    me = await bot.get_me()
    logger.info('Bot started as @%s', me.username)
    ensure_media_dir()

async def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.startup.register(on_startup)
    # include routers
    dp.include_router(admin.router)
    dp.include_router(media.router)
    dp.include_router(safety.router)
    dp.include_router(owner.router)

    @dp.message(F.text == '/help')
    async def help_cmd(m: Message):
        txt = ('Ultimate Bot — commands:\n'
               '/help - this message\n'
               'Admin: /ban /kick /mute /unmute /warn /purge /setrules\n'
               'Media: /upload (attach), /find <q>, /send <idx>\n'
               'Safety: /sos /silent /trust add/list\n'
               'Owner: /stats /logs /backup') 
        await m.answer(txt)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    init_db()
    asyncio.run(main())
