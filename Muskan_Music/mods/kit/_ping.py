# © @MuskanBot

from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message
from config import *
from Muskan_Music import app
from Muskan_Music.engine._vclient import Muskan
from Muskan_Music.helpers import bot_sys_stats
from Muskan_Music.helpers.wrap._lang import language
from Muskan_Music.helpers.kb import supp_markup
from config import BANNED_USERS

@app.on_message(filters.command("ping", prefixes=["/"]) & ~BANNED_USERS)
@language
async def ping_com(client, message: Message, _):
    start = datetime.now()
   
    response = await message.reply(
        text=_["ping_1"].format(app.mention),
    )
    pytgping = await Muskan.ping()
    UP, CPU, RAM, DISK = await bot_sys_stats()
    resp = (datetime.now() - start).microseconds / 1000
    await response.edit_text(
        _["ping_2"].format(resp, app.mention, UP, RAM, CPU, DISK, pytgping),
        reply_markup=supp_markup(_),
    )