# © @MuskanBot

from pyrogram.enums import ParseMode

from Muskan_Music import app
from Muskan_Music.helpers._store import is_on_off
from config import LOGGER_ID

async def play_logs(message, streamtype):
    if await is_on_off(2):
        logger_text = f"""
<b>{app.mention} ᴘʟᴀʏ ʟᴏɢ</b>

<b>ᴄʜᴀᴛ ɪᴅ :</b> <code>{message.chat.id}</code>
<b>ᴄʜᴀᴛ ɴᴀᴍᴇ :</b> {message.chat.title}
<b>ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.chat.username}

<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>
<b>ɴᴀᴍᴇ :</b> {message.from_user.mention}
<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}

<b>ǫᴜᴇʀʏ :</b> {message.text.split(None, 1)[1]}
<b>sᴛʀᴇᴀᴍᴛʏᴘᴇ :</b> {streamtype}"""
        if message.chat.id != LOGGER_ID:
            try:
                await app.send_message(
                    chat_id=LOGGER_ID,
                    text=logger_text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
            except:
                pass
        return


async def _get_chat_link(chat_id):
    """Return public link or exported invite link, or 'None' string."""
    try:
        chat = await app.get_chat(chat_id)
        if getattr(chat, "username", None):
            return f"https://t.me/{chat.username}", chat
        try:
            link = await app.export_chat_invite_link(chat_id)
            return link, chat
        except Exception:
            return "None", chat
    except Exception:
        return "None", None


async def stream_log(chat_id, original_chat_id, title, user_name, user_id, log_type, position=None):
    """Send play/queue log to logger group.
    log_type: 'play' or 'queue'
    """
    if not LOGGER_ID or original_chat_id == LOGGER_ID:
        return
    try:
        chat_link, chat = await _get_chat_link(original_chat_id)
        chat_title = (chat.title if chat else None) or "Unknown"
        members = (getattr(chat, "members_count", None) if chat else None) or "N/A"
        type_line = (
            "🎵 ᴘʟᴀʏ"
            if log_type == "play"
            else f"📋 ǫᴜᴇᴜᴇ  •  ᴘᴏsɪᴛɪᴏɴ #{position}"
        )
        log_text = (
            f"<b>🎶 {app.mention} sᴛʀᴇᴀᴍ ʟᴏɢ</b>\n\n"
            f"<b>ᴛʏᴘᴇ  :</b>  {type_line}\n"
            f"<b>sᴏɴɢ  :</b>  {title}\n\n"
            f"<b>ᴄʜᴀᴛ ɴᴀᴍᴇ  :</b>  {chat_title}\n"
            f"<b>ᴄʜᴀᴛ ʟɪɴᴋ  :</b>  {chat_link}\n"
            f"<b>ᴍᴇᴍʙᴇʀs  :</b>  {members}\n\n"
            f"<b>ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ  :</b>  {user_name}\n"
            f"<b>ᴜsᴇʀ ɪᴅ  :</b>  <code>{user_id}</code>"
        )
        await app.send_message(
            chat_id=LOGGER_ID,
            text=log_text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except Exception:
        pass


async def chat_log(chat_id, action):
    """Send bot join/leave log to logger group.
    action: 'join' or 'leave'
    """
    if not LOGGER_ID or chat_id == LOGGER_ID:
        return
    try:
        chat_link, chat = await _get_chat_link(chat_id)
        chat_title = (chat.title if chat else None) or "Unknown"
        members = (getattr(chat, "members_count", None) if chat else None) or "N/A"
        action_text = "✅ ʙᴏᴛ ᴀᴅᴅᴇᴅ" if action == "join" else "❌ ʙᴏᴛ ʀᴇᴍᴏᴠᴇᴅ / ʟᴇꜰᴛ"
        log_text = (
            f"<b>🤖 {app.mention} ᴄʜᴀᴛ ʟᴏɢ</b>\n\n"
            f"<b>ᴀᴄᴛɪᴏɴ  :</b>  {action_text}\n"
            f"<b>ᴄʜᴀᴛ ɴᴀᴍᴇ  :</b>  {chat_title}\n"
            f"<b>ᴄʜᴀᴛ ʟɪɴᴋ  :</b>  {chat_link}\n"
            f"<b>ᴍᴇᴍʙᴇʀs  :</b>  {members}\n"
            f"<b>ᴄʜᴀᴛ ɪᴅ  :</b>  <code>{chat_id}</code>"
        )
        await app.send_message(
            chat_id=LOGGER_ID,
            text=log_text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except Exception:
        pass