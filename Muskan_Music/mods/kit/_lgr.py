# © @MuskanBot

from pyrogram import filters
from pyrogram.types import Message

from Muskan_Music import app
from Muskan_Music.helpers._store import get_vcnotify, set_vcnotify

prefixes = [".", "!", "/", "@", "?", "'"]

@app.on_message(filters.group & ~filters.bot & ~filters.via_bot, group=68)
async def auto_vc_notify(_, message: Message):
    chat_id = message.chat.id
    try:
        from Muskan_Music.engine._vclient import Muskan, vc_join_monitors
        task = vc_join_monitors.get(chat_id)
        if task and not task.done():
            return
        if not await get_vcnotify(chat_id):
            return
        await Muskan.maybe_start_vc_join_notifier(chat_id, chat_id)
    except Exception:
        pass

@app.on_message(
    filters.video_chat_started | filters.video_chat_members_invited,
    group=69,
)
async def auto_activate_vc_logger(_, message: Message):
    chat_id = message.chat.id
    try:
        if not await get_vcnotify(chat_id):
            return
        from Muskan_Music.engine._vclient import Muskan
        await Muskan.maybe_start_vc_join_notifier(chat_id, chat_id)
    except Exception:
        pass

@app.on_message(
    filters.command("vclogger", prefixes=prefixes) & filters.group
)
async def vclogger_toggle(_, message: Message):
    chat_id = message.chat.id

    if len(message.command) < 2:
        status = await get_vcnotify(chat_id)
        state_str = "✅ ᴇɴᴀʙʟᴇᴅ" if status else "❌ ᴅɪsᴀʙʟᴇᴅ"
        return await message.reply_text(
            f"📡 <b>VC Logger</b> is currently <b>{state_str}</b>\n\n"
            f"Use <code>/vclogger on</code> or <code>/vclogger off</code>",
            quote=True,
        )

    state = message.command[1].lower() in ("on", "enable", "enabled", "yes")
    await set_vcnotify(chat_id, state)

    from Muskan_Music.engine._vclient import Muskan

    if state:
        await Muskan.maybe_start_vc_join_notifier(chat_id, chat_id)
        await message.reply_text(
            "✅ <b>VC Logger Enabled!</b>\n\n"
            "🎤 I will notify whenever someone joins or leaves the voice chat.",
            quote=True,
        )
    else:
        await Muskan.stop_vc_join_notifier(chat_id)
        await message.reply_text(
            "🚫 <b>VC Logger Disabled.</b>",
            quote=True,
        )
