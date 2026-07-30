# © @MuskanBot

from pyrogram import filters
from pyrogram.types import Message

from Muskan_Music import app
from Muskan_Music.helpers._store import get_autoplay, get_cmode, set_autoplay
from Muskan_Music.helpers.wrap import AdminRightsCheck
from Muskan_Music.helpers.kb import close_markup
from config import BANNED_USERS


@app.on_message(
    filters.command(["autoplay", "cautoplay"]) & filters.group & ~BANNED_USERS
)
@AdminRightsCheck
async def autoplay_control(cli, message: Message, _, chat_id):
    command = message.command[0].lower()

    # Channel-linked autoplay
    if command.startswith("c"):
        chat_id = await get_cmode(message.chat.id)
        if chat_id is None:
            return await message.reply_text(_["setting_7"])
        try:
            await cli.get_chat(chat_id)
        except Exception:
            return await message.reply_text(_["cplay_4"])

    # Show current status if no argument given
    if len(message.command) == 1:
        status = "enabled" if await get_autoplay(chat_id) else "disabled"
        return await message.reply_text(
            _["autoplay_3"].format(status),
            reply_markup=close_markup(_),
        )

    state = message.text.split(None, 1)[1].strip().lower()

    if state in {"on", "enable", "enabled", "yes"}:
        await set_autoplay(chat_id, True)
        return await message.reply_text(
            _["autoplay_1"].format(message.from_user.mention),
            reply_markup=close_markup(_),
        )

    if state in {"off", "disable", "disabled", "no"}:
        await set_autoplay(chat_id, False)
        return await message.reply_text(
            _["autoplay_2"].format(message.from_user.mention),
            reply_markup=close_markup(_),
        )

    return await message.reply_text(_["autoplay_4"], reply_markup=close_markup(_))
