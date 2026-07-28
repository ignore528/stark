# © @MuskanBot

import asyncio
import re
import time

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    FloodWait,
    MessageDeleteForbidden,
    PeerIdInvalid,
    UserDeactivated,
    UserDeactivatedBan,
    UsernameNotOccupied,
)
from pyrogram.types import Message

from Muskan_Music import app
from Muskan_Music.misc import SUDOERS
from Muskan_Music.helpers._store import (
    get_biodetect,
    get_lang,
    set_biodetect,
)
from config import BANNED_USERS, OWNER_ID
from strings import get_string

prefixes = [".", "!", "/", "@", "?", "'"]

_LINK_RE = re.compile(
    r"""
    (?:
        https?://[^\s]+              # http:// or https://
      | www\.[^\s]{2,}              # www.something
      | t\.me/[^\s]+                # t.me/ deep links
      | @[A-Za-z]\w{3,}            # @username (≥5 chars, looks like promo)
      | [A-Za-z0-9]                 # bare domain start
        [A-Za-z0-9\-]{0,61}
        [A-Za-z0-9]
        \.(?:com|net|org|io|xyz|me|info|biz|co|app|dev|club|shop|site|online|store|live|top|pro|vip|gg)
        (?:/[^\s]*)?
    )
    """,
    re.VERBOSE | re.IGNORECASE,
)

_bio_cache: dict[tuple, tuple] = {}   # (chat_id, user_id) -> (has_link: bool, ts: float)
_CACHE_MAX = 500
_CACHE_TTL = 300  # re-check bio every 5 minutes

def _has_link(text: str) -> bool:
    return bool(_LINK_RE.search(text))

async def _is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR)
    except Exception:
        return False

async def _get_bio(user_id: int) -> str | None:
    """
    Fetch user bio via GetFullUser (users.getFullUser MTProto call).
    get_users() only calls GetUsers which does NOT return bio.
    get_chat() calls GetFullUser which populates chat.bio from full_user.about.
    """
    try:
        chat = await app.get_chat(user_id)
        return chat.bio or ""
    except (PeerIdInvalid, UserDeactivated, UserDeactivatedBan,
            UsernameNotOccupied, KeyError):
        return ""
    except FloodWait as e:
        await asyncio.sleep(min(e.value, 10))
        return None
    except Exception:
        return None

@app.on_message(
    filters.group & ~filters.bot & ~filters.via_bot & ~BANNED_USERS,
    group=70,
)
async def bio_link_detector(_, message: Message):
    if not message.from_user:
        return

    chat_id  = message.chat.id
    user_id  = message.from_user.id

    if user_id in SUDOERS:
        return

    if not await get_biodetect(chat_id):
        return

    if await _is_admin(chat_id, user_id):
        return

    cache_key = (chat_id, user_id)
    cached = _bio_cache.get(cache_key)

    bio_has_link = None
    if cached is not None:
        cached_val, cached_ts = cached
        if time.monotonic() - cached_ts < _CACHE_TTL:
            bio_has_link = cached_val

    if bio_has_link is None:
        bio = await _get_bio(user_id)
        if bio is None:
            return
        bio_has_link = _has_link(bio)
        if len(_bio_cache) >= _CACHE_MAX:
            for old_key in list(_bio_cache)[:50]:
                _bio_cache.pop(old_key, None)
        _bio_cache[cache_key] = (bio_has_link, time.monotonic())

    if not bio_has_link:
        return

    try:
        await message.delete()
    except (MessageDeleteForbidden, ChatAdminRequired):
        pass
    except Exception:
        pass

    lang = await get_lang(chat_id)
    _   = get_string(lang)

    mention = message.from_user.mention
    warn_text = _["bio_detect_1"].format(mention=mention)

    try:
        sent = await app.send_message(chat_id, warn_text)
        await asyncio.sleep(20)
        await sent.delete()
    except Exception:
        pass

@app.on_message(
    filters.command("biodetect", prefixes=prefixes) & filters.group & ~BANNED_USERS,
)
async def biodetect_toggle(_, message: Message):
    chat_id = message.chat.id

    if not message.from_user:
        return

    user_id = message.from_user.id
    is_admin = await _is_admin(chat_id, user_id)
    sudo_ids: set = getattr(SUDOERS, "user_ids", set())
    is_sudo  = (user_id in sudo_ids) or (user_id == OWNER_ID)

    if not is_admin and not is_sudo:
        lang = await get_lang(chat_id)
        _    = get_string(lang)
        return await message.reply_text(
            "<b>⊘ Access Denied</b>\n\n"
            "▸ Only group <b>admins</b> can toggle Bio Link Guard.",
            quote=True,
        )

    lang = await get_lang(chat_id)
    _   = get_string(lang)

    if len(message.command) < 2:
        status = await get_biodetect(chat_id)
        state_str = _["bio_detect_on"] if status else _["bio_detect_off"]
        return await message.reply_text(
            _["bio_detect_2"].format(state=state_str),
            quote=True,
        )

    state = message.command[1].lower() in ("on", "enable", "enabled", "yes")
    await set_biodetect(chat_id, state)

    for key in [k for k in _bio_cache if k[0] == chat_id]:
        _bio_cache.pop(key, None)

    if state:
        await message.reply_text(_["bio_detect_3"], quote=True)
    else:
        await message.reply_text(_["bio_detect_4"], quote=True)
