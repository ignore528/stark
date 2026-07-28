# © @MuskanBot

import asyncio
import time
import random
from pyrogram import filters, enums
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from py_yt import VideosSearch

import config
from Muskan_Music import app
from Muskan_Music.misc import _boot_
from Muskan_Music.mods.root._sudo import sudoers_list
from Muskan_Music.helpers._store import get_served_chats, get_served_users, get_sudoers
from Muskan_Music.helpers import bot_sys_stats
from Muskan_Music.helpers._store import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from Muskan_Music.helpers.wrap._lang import LanguageStart
from Muskan_Music.helpers._fmt import get_readable_time
from Muskan_Music.helpers.kb import help_pannel, private_panel, start_panel
from Muskan_Music.helpers._log import chat_log
from config import BANNED_USERS
from strings import get_string

YUMI_PICS = [
config.START_IMG_URL,
]

# Random emojis for reaction on user's /start message
# Verified: Message.react(emoji) is available in Kurigram
VALID_EMOJII = ["🔥", "💋", "🥺", "😒", "💖", "💘", "💕", "✨", "🥰", "🍌", "💔", "😓", "🫧"]

# Telegram premium message effect IDs (fire, confetti, balloons, love)
# Verified: send_photo(..., effect_id=...) is the correct param in Kurigram
EFFECT_IDS = [
    5046509860389126442,
    5107584321108051014,
    5104841245755180586,
    5159385139981059251,
]

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name[0:4] == "help":
            keyboard = help_pannel(_)
            return await message.reply_photo(
                random.choice(YUMI_PICS),
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=keyboard,
            )
        if name[0:3] == "sud":
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"✦ {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>sᴜᴅᴏʟɪsᴛ</b>.\n\n<b>✦ ᴜsᴇʀ ɪᴅ ➠</b> <code>{message.from_user.id}</code>\n<b>✦ ᴜsᴇʀɴᴀᴍᴇ ➠</b> @{message.from_user.username}",
                )
            return
        if name[0:3] == "inf":
            m = await message.reply_text("🔎")
            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]
            searched_text = _["start_6"].format(
                title, duration, views, published, channellink, channel, app.mention
            )
            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=_["S_B_8"], url=link),
                        InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_CHAT),
                    ],
                ]
            )
            await m.delete()
            await app.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                reply_markup=key,
            )
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"✦ {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>ᴛʀᴀᴄᴋ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b>.\n\n✦ <b>ᴜsᴇʀ ɪᴅ ➠</b> <code>{message.from_user.id}</code>\n✦ <b>ᴜsᴇʀɴᴀᴍᴇ ➠</b> @{message.from_user.username}",
                )
    else:
        out = private_panel(_)
        served_chats = len(await get_served_chats())
        served_users = len(await get_served_users())
        UP, CPU, RAM, DISK = await bot_sys_stats()
        # Reaction on user's /start message
        # Message.react(emoji) verified available in Kurigram
        try:
            await message.react(random.choice(VALID_EMOJII))
        except Exception:
            pass
        # Loading animation while data loads
        try:
            await app.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_PHOTO)
        except Exception:
            pass
        # Send start photo with premium effect
        # send_photo(effect_id=...) verified in Kurigram (not message_effect_id)
        caption = _["start_2"].format(
            message.from_user.mention, app.mention, UP, DISK, CPU, RAM, served_users, served_chats
        )
        try:
            await app.send_photo(
                chat_id=message.chat.id,
                photo=random.choice(YUMI_PICS),
                caption=caption,
                reply_markup=InlineKeyboardMarkup(out),
                effect_id=random.choice(EFFECT_IDS),
            )
        except Exception:
            await message.reply_photo(
                random.choice(YUMI_PICS),
                caption=caption,
                reply_markup=InlineKeyboardMarkup(out),
            )
        if await is_on_off(2):
            return await app.send_message(
                chat_id=config.LOGGER_ID,
                text=f"✦ {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n✦ <b>ᴜsᴇʀ ɪᴅ ➠</b> <code>{message.from_user.id}</code>\n✦ <b>ᴜsᴇʀɴᴀᴍᴇ ➠</b> @{message.from_user.username}",
            )

@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - _boot_)
    await message.reply_photo(
        random.choice(YUMI_PICS),
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(out),
    )
    return await add_served_chat(message.chat.id)

@app.on_callback_query(filters.regex("^go_to_start$") & ~BANNED_USERS)
async def go_to_start_cb(client, query):
    try:
        await query.answer()
    except:
        pass
    try:
        chat_id = query.message.chat.id
        language = await get_lang(chat_id)
        _ = get_string(language)
        out = private_panel(_)
        served_chats = len(await get_served_chats())
        served_users = len(await get_served_users())
        UP, CPU, RAM, DISK = await bot_sys_stats()
        caption = _["start_2"].format(
            query.from_user.mention, app.mention, UP, DISK, CPU, RAM, served_users, served_chats
        )
        try:
            await query.edit_message_caption(
                caption=caption,
                reply_markup=InlineKeyboardMarkup(out),
            )
        except Exception:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(out)
            )
    except Exception:
        pass

@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass
            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)
                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                await message.reply_text(
                    text=_["start_3"].format(
                        message.from_user.mention,
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                await add_served_chat(message.chat.id)
                asyncio.create_task(chat_log(message.chat.id, "join"))
                await message.stop_propagation()
        except Exception as ex:
            print(ex)


@app.on_message(filters.left_chat_member, group=-1)
async def left_handler(client, message: Message):
    try:
        if message.left_chat_member and message.left_chat_member.id == app.id:
            asyncio.create_task(chat_log(message.chat.id, "leave"))
    except Exception:
        pass