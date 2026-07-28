# © @MuskanBot

from pyrogram import filters
from pyrogram.types import Message

from Muskan_Music import app
from Muskan_Music.engine._vclient import Muskan
from Muskan_Music.helpers._store import set_loop
from Muskan_Music.helpers.wrap import AdminRightsCheck
from Muskan_Music.helpers.kb import close_markup
from config import BANNED_USERS

@app.on_message(
    filters.command(["end", "stop", "cend", "cstop"], prefixes=["/", "!", "%", ",", "", ".", "@", "#"]) & filters.group & ~BANNED_USERS
)
@AdminRightsCheck
async def stop_music(cli, message: Message, _, chat_id):
    if not len(message.command) == 1:
        return
    await Muskan.stop_stream(chat_id)
    await set_loop(chat_id, 0)
    await message.reply_text(
        _["admin_5"].format(message.from_user.mention), reply_markup=close_markup(_)
    )