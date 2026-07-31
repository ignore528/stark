# © @MuskanBot

import asyncio
import os
import time
from datetime import datetime, timedelta
from typing import Union

from pyrogram import Client
from pyrogram.enums import ChatType
from pyrogram.handlers import RawUpdateHandler
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.functions.messages import GetFullChat
from pyrogram.raw.types import PeerUser, UpdateGroupCall, UpdateGroupCallParticipants
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls
from pytgcalls.exceptions import (
    NoActiveGroupCall,
    NotInCallError as AlreadyJoinedError,
)
TelegramServerError = Exception
from pytgcalls.types import Update
from pytgcalls.types import MediaStream, AudioQuality, VideoQuality
from pytgcalls.types.stream import StreamEnded

import config
from Muskan_Music import LOGGER, YouTube, app
from Muskan_Music.misc import db
from Muskan_Music.helpers._store import (
    add_active_chat,
    add_active_video_chat,
    get_autoplay,
    get_lang,
    get_loop,
    get_vcnotify,
    group_assistant,
    is_autoend,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from Muskan_Music.helpers._exc import AssistantErr
from Muskan_Music.helpers._fmt import check_duration, seconds_to_min, speed_converter
from Muskan_Music.helpers.kb._play import stream_markup
from Muskan_Music.helpers.flow._aclear import auto_clean
from Muskan_Music.helpers._thumb import get_thumb
from strings import get_string

autoend = {}
counter = {}
# Per-chat rolling history of recently played video IDs for autoplay deduplication
_autoplay_history: dict = {}
_AUTOPLAY_HISTORY_MAX = 20

vc_join_monitors:     dict[int, asyncio.Task] = {}
vc_join_snapshots:    dict[int, set]          = {}
vc_join_targets:      dict[int, int]          = {}
vc_join_call_map:     dict[int, dict]         = {}
vc_join_event_cache:  dict                    = {}
vc_join_notice_cache: dict                    = {}
vc_left_event_cache:  dict                    = {}
vc_left_notice_cache: dict                    = {}

async def _auto_delete(msg, delay: int = 10) -> None:
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except Exception:
        pass

async def _clear_(chat_id):
    db[chat_id] = []
    for call_id, info in list(vc_join_call_map.items()):
        if info.get("chat_id") == chat_id:
            vc_join_call_map.pop(call_id, None)
    task = vc_join_monitors.pop(chat_id, None)
    if task and not task.done():
        task.cancel()
    vc_join_snapshots.pop(chat_id, None)
    vc_join_targets.pop(chat_id, None)
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)

class Call(PyTgCalls):
    def __init__(self):
        self.userbot1 = Client(
            name="Muskan_Ass1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
        )
        self.one = PyTgCalls(
            self.userbot1,
            cache_duration=150,
        )

    async def pause_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.pause(chat_id)

    async def resume_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.resume(chat_id)

    async def stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await _clear_(chat_id)
            await assistant.leave_call(chat_id)
        except:
            pass

    async def stop_stream_force(self, chat_id: int):
        try:
            if config.STRING1:
                await self.one.leave_call(chat_id)
        except:
            pass
        try:
            await _clear_(chat_id)
        except:
            pass

    async def speedup_stream(self, chat_id: int, file_path, speed, playing):
        assistant = await group_assistant(self, chat_id)
        if str(speed) != str("1.0"):
            base = os.path.basename(file_path)
            chatdir = os.path.join(os.getcwd(), "playback", str(speed))
            if not os.path.isdir(chatdir):
                os.makedirs(chatdir)
            out = os.path.join(chatdir, base)
            if not os.path.isfile(out):
                if str(speed) == str("0.5"):
                    vs = 2.0
                if str(speed) == str("0.75"):
                    vs = 1.35
                if str(speed) == str("1.5"):
                    vs = 0.68
                if str(speed) == str("2.0"):
                    vs = 0.5
                proc = await asyncio.create_subprocess_shell(
                    cmd=(
                        "ffmpeg "
                        "-i "
                        f"{file_path} "
                        "-filter:v "
                        f"setpts={vs}*PTS "
                        "-filter:a "
                        f"atempo={speed} "
                        f"{out}"
                    ),
                    stdin=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await proc.communicate()
            else:
                pass
        else:
            out = file_path
        dur = await asyncio.get_event_loop().run_in_executor(None, check_duration, out)
        dur = int(dur)
        played, con_seconds = speed_converter(playing[0]["played"], speed)
        duration = seconds_to_min(dur)
        stream = (
            MediaStream(
                out,
                audio_parameters=AudioQuality.HIGH,
                video_parameters=VideoQuality.SD_480p,
                ffmpeg_parameters=f"-ss {played} -to {duration}",
            )
            if playing[0]["streamtype"] == "video"
            else MediaStream(
                out,
                audio_parameters=AudioQuality.HIGH,
                video_flags=MediaStream.Flags.IGNORE,
                ffmpeg_parameters=f"-ss {played} -to {duration}",
            )
        )
        if str(db[chat_id][0]["file"]) == str(file_path):
            await assistant.play(chat_id, stream)
        else:
            raise AssistantErr("Umm")
        if str(db[chat_id][0]["file"]) == str(file_path):
            exis = (playing[0]).get("old_dur")
            if not exis:
                db[chat_id][0]["old_dur"] = db[chat_id][0]["dur"]
                db[chat_id][0]["old_second"] = db[chat_id][0]["seconds"]
            db[chat_id][0]["played"] = con_seconds
            db[chat_id][0]["dur"] = duration
            db[chat_id][0]["seconds"] = dur
            db[chat_id][0]["speed_path"] = out
            db[chat_id][0]["speed"] = speed

    async def force_stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            check = db.get(chat_id)
            check.pop(0)
        except:
            pass
        await remove_active_video_chat(chat_id)
        await remove_active_chat(chat_id)
        try:
            await assistant.leave_call(chat_id)
        except:
            pass

    async def skip_stream(
        self,
        chat_id: int,
        link: str,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        assistant = await group_assistant(self, chat_id)
        if video:
            stream = MediaStream(
                link,
                audio_parameters=AudioQuality.HIGH,
                video_parameters=VideoQuality.SD_480p,
            )
        else:
            stream = MediaStream(link, audio_parameters=AudioQuality.HIGH, video_flags=MediaStream.Flags.IGNORE)
        await assistant.play(
            chat_id,
            stream,
        )

    async def seek_stream(self, chat_id, file_path, to_seek, duration, mode):
        assistant = await group_assistant(self, chat_id)
        stream = (
            MediaStream(
                file_path,
                audio_parameters=AudioQuality.HIGH,
                video_parameters=VideoQuality.SD_480p,
                ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
            )
            if mode == "video"
            else MediaStream(
                file_path,
                audio_parameters=AudioQuality.HIGH,
                video_flags=MediaStream.Flags.IGNORE,
                ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
            )
        )
        await assistant.play(chat_id, stream)

    async def stream_call(self, link):
        assistant = await group_assistant(self, config.LOGGER_ID)
        await assistant.play(config.LOGGER_ID, MediaStream(link))
        await asyncio.sleep(0.2)
        await assistant.leave_call(config.LOGGER_ID)

    async def join_call(
        self,
        chat_id: int,
        original_chat_id: int,
        link,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        assistant = await group_assistant(self, chat_id)
        language = await get_lang(chat_id)
        _ = get_string(language)
        if video:
            stream = MediaStream(
                link,
                audio_parameters=AudioQuality.HIGH,
                video_parameters=VideoQuality.SD_480p,
            )
        else:
            stream = (
                MediaStream(
                    link,
                    audio_parameters=AudioQuality.HIGH,
                    video_parameters=VideoQuality.SD_480p,
                )
                if video
                else MediaStream(link, audio_parameters=AudioQuality.HIGH, video_flags=MediaStream.Flags.IGNORE)
            )
        try:
            await assistant.play(chat_id, stream)
        except NoActiveGroupCall:
            raise AssistantErr(_["call_8"])
        except AlreadyJoinedError:
            raise AssistantErr(_["call_9"])
        except TelegramServerError:
            raise AssistantErr(_["call_10"])
        await add_active_chat(chat_id)
        await music_on(chat_id)
        if video:
            await add_active_video_chat(chat_id)
        if await is_autoend():
            counter[chat_id] = {}
            users = len(await assistant.get_participants(chat_id))
            if users == 1:
                autoend[chat_id] = datetime.now() + timedelta(minutes=1)

    async def _enqueue_autoplay_track(self, chat_id: int, finished_track: dict) -> bool:
        """Queue ka khatam hone par ek related YouTube track fetch karke db mein add karo."""
        if not finished_track:
            return False
        if not await get_autoplay(chat_id):
            return False

        vidid = str(finished_track.get("vidid") or "")
        file_ = str(finished_track.get("file") or "")
        # live streams aur non-YouTube tracks ke liye autoplay nahi
        if not vidid or vidid in {"telegram", "soundcloud"}:
            return False
        if file_.startswith("live_") or file_.startswith("index_"):
            return False

        title = finished_track.get("title", "")
        streamtype = finished_track.get("streamtype", "audio")
        original_chat_id = finished_track.get("chat_id", chat_id)

        # Build exclude set from rolling history
        history = _autoplay_history.get(chat_id, [])
        exclude_ids = set(history)
        exclude_ids.add(vidid)

        try:
            recommendation = await YouTube.autoplay(vidid, title, exclude_ids=exclude_ids)
        except Exception:
            recommendation = None

        if not recommendation:
            return False

        # Record in per-chat history (dedup rolling window)
        hist = _autoplay_history.setdefault(chat_id, [])
        hist.append(vidid)
        if len(hist) > _AUTOPLAY_HISTORY_MAX:
            hist.pop(0)

        # Enqueue the recommended track
        db.setdefault(chat_id, []).append({
            "title": recommendation["title"].title(),
            "dur": recommendation["duration_min"],
            "streamtype": streamtype,
            "by": "AutoPlay 🔁",
            "user_id": 0,
            "chat_id": original_chat_id,
            "file": f"vid_{recommendation['vidid']}",
            "vidid": recommendation["vidid"],
            "seconds": recommendation["duration_sec"],
            "played": 0,
        })
        return True

    async def change_stream(self, client, chat_id):
        check = db.get(chat_id)
        popped = None
        loop = await get_loop(chat_id)
        try:
            if loop == 0:
                popped = check.pop(0)
            else:
                loop = loop - 1
                await set_loop(chat_id, loop)
            await auto_clean(popped)
            if not check:
                # ── AutoPlay: queue khatam hone par related track fetch karo ──
                enqueued = await self._enqueue_autoplay_track(chat_id, popped)
                if enqueued:
                    check = db.get(chat_id)
                if not check:
                    await _clear_(chat_id)
                    return await client.leave_call(chat_id)
        except:
            try:
                await _clear_(chat_id)
                return await client.leave_call(chat_id)
            except:
                return
        else:
            queued = check[0]["file"]
            language = await get_lang(chat_id)
            _ = get_string(language)
            title = (check[0]["title"]).title()
            user = check[0]["by"]
            original_chat_id = check[0]["chat_id"]
            streamtype = check[0]["streamtype"]
            videoid = check[0]["vidid"]
            db[chat_id][0]["played"] = 0
            exis = (check[0]).get("old_dur")
            if exis:
                db[chat_id][0]["dur"] = exis
                db[chat_id][0]["seconds"] = check[0]["old_second"]
                db[chat_id][0]["speed_path"] = None
                db[chat_id][0]["speed"] = 1.0
            video = True if str(streamtype) == "video" else False
            if "live_" in queued:
                n, link = await YouTube.video(videoid, True)
                if n == 0:
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )
                if video:
                    stream = MediaStream(
                        link,
                        audio_parameters=AudioQuality.HIGH,
                        video_parameters=VideoQuality.SD_480p,
                    )
                else:
                    stream = MediaStream(
                        link,
                        audio_parameters=AudioQuality.HIGH,
                        video_flags=MediaStream.Flags.IGNORE,
                    )
                try:
                    await client.play(chat_id, stream)
                except Exception:
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )
                img = await get_thumb(videoid)
                button = stream_markup(_, chat_id)
                run = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=img,
                    caption=_["stream_1"].format(
                        f"https://t.me/{app.username}?start=info_{videoid}",
                        title[:23],
                        check[0]["dur"],
                        user,
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
            elif "vid_" in queued:
                mystic = await app.send_message(original_chat_id, _["call_7"])
                try:
                    file_path, direct = await YouTube.download(
                        videoid,
                        mystic,
                        videoid=True,
                        video=True if str(streamtype) == "video" else False,
                    )
                except:
                    return await mystic.edit_text(
                        _["call_6"], disable_web_page_preview=True
                    )
                if video:
                    stream = MediaStream(
                        file_path,
                        audio_parameters=AudioQuality.HIGH,
                        video_parameters=VideoQuality.SD_480p,
                    )
                else:
                    stream = MediaStream(
                        file_path,
                        audio_parameters=AudioQuality.HIGH,
                        video_flags=MediaStream.Flags.IGNORE,
                    )
                try:
                    await client.play(chat_id, stream)
                except:
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )
                img = await get_thumb(videoid)
                button = stream_markup(_, chat_id)
                await mystic.delete()
                run = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=img,
                    caption=_["stream_1"].format(
                        f"https://t.me/{app.username}?start=info_{videoid}",
                        title[:23],
                        check[0]["dur"],
                        user,
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"
            elif "index_" in queued:
                stream = (
                    MediaStream(
                        videoid,
                        audio_parameters=AudioQuality.HIGH,
                        video_parameters=VideoQuality.SD_480p,
                    )
                    if str(streamtype) == "video"
                    else MediaStream(videoid, audio_parameters=AudioQuality.HIGH, video_flags=MediaStream.Flags.IGNORE)
                )
                try:
                    await client.play(chat_id, stream)
                except:
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )
                button = stream_markup(_, chat_id)
                run = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=config.STREAM_IMG_URL,
                    caption=_["stream_2"].format(user),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
            else:
                if video:
                    stream = MediaStream(
                        queued,
                        audio_parameters=AudioQuality.HIGH,
                        video_parameters=VideoQuality.SD_480p,
                    )
                else:
                    stream = MediaStream(
                        queued,
                        audio_parameters=AudioQuality.HIGH,
                        video_flags=MediaStream.Flags.IGNORE,
                    )
                try:
                    await client.play(chat_id, stream)
                except:
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )
                if videoid == "telegram":
                    button = stream_markup(_, chat_id)
                    run = await app.send_photo(
                        chat_id=original_chat_id,
                        photo=config.TELEGRAM_AUDIO_URL
                        if str(streamtype) == "audio"
                        else config.TELEGRAM_VIDEO_URL,
                        caption=_["stream_1"].format(
                            config.SUPPORT_CHAT, title[:23], check[0]["dur"], user
                        ),
                        reply_markup=InlineKeyboardMarkup(button),
                    )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "tg"
                elif videoid == "soundcloud":
                    button = stream_markup(_, chat_id)
                    run = await app.send_photo(
                        chat_id=original_chat_id,
                        photo=config.SOUNCLOUD_IMG_URL,
                        caption=_["stream_1"].format(
                            config.SUPPORT_CHAT, title[:23], check[0]["dur"], user
                        ),
                        reply_markup=InlineKeyboardMarkup(button),
                    )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "tg"
                else:
                    img = await get_thumb(videoid)
                    button = stream_markup(_, chat_id)
                    run = await app.send_photo(
                        chat_id=original_chat_id,
                        photo=img,
                        caption=_["stream_1"].format(
                            f"https://t.me/{app.username}?start=info_{videoid}",
                            title[:23],
                            check[0]["dur"],
                            user,
                        ),
                        reply_markup=InlineKeyboardMarkup(button),
                    )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "stream"

    async def _resolve_vc_call_id(self, chat_id: int) -> int | None:
        try:
            chat = await app.get_chat(chat_id)
        except Exception:
            return None
        try:
            if chat.type in {ChatType.SUPERGROUP, ChatType.CHANNEL}:
                full = await app.invoke(
                    GetFullChannel(channel=await app.resolve_peer(chat_id))
                )
            else:
                full = await app.invoke(GetFullChat(chat_id=abs(int(chat_id))))
        except Exception:
            return None
        call = getattr(getattr(full, "full_chat", None), "call", None)
        if not call:
            return None
        return int(call.id)

    @staticmethod
    def _extract_user_id_from_peer(peer) -> int | None:
        if isinstance(peer, PeerUser):
            return int(peer.user_id)
        return None

    @staticmethod
    def _remember_join_event(call_id: int, user_id: int, date: int, source: int) -> bool:
        now = time.monotonic()
        for key, stamp in list(vc_join_event_cache.items()):
            if now - stamp > 30:
                vc_join_event_cache.pop(key, None)
        event_key = (call_id, user_id, date, source, "join")
        if event_key in vc_join_event_cache:
            return False
        vc_join_event_cache[event_key] = now
        return True

    @staticmethod
    def _remember_join_notice(notify_chat_id: int, user_id: int, date: int, source: int) -> bool:
        # date=0 means monitor-loop path — snapshot diff already handles dedup, always allow
        if date == 0:
            return True
        now = time.monotonic()
        for key, stamp in list(vc_join_notice_cache.items()):
            if now - stamp > 5:
                vc_join_notice_cache.pop(key, None)
        # include date so the same user rejoining (new date) always triggers a notice
        notice_key = (notify_chat_id, user_id, "join", date)
        if notice_key in vc_join_notice_cache:
            return False
        vc_join_notice_cache[notice_key] = now
        return True

    @staticmethod
    def _remember_left_event(call_id: int, user_id: int, date: int, source: int) -> bool:
        now = time.monotonic()
        for key, stamp in list(vc_left_event_cache.items()):
            if now - stamp > 30:
                vc_left_event_cache.pop(key, None)
        event_key = (call_id, user_id, date, source, "left")
        if event_key in vc_left_event_cache:
            return False
        vc_left_event_cache[event_key] = now
        return True

    @staticmethod
    def _remember_left_notice(notify_chat_id: int, user_id: int, date: int, source: int) -> bool:
        # date=0 means monitor-loop path — snapshot diff already handles dedup, always allow
        if date == 0:
            return True
        now = time.monotonic()
        for key, stamp in list(vc_left_notice_cache.items()):
            if now - stamp > 5:
                vc_left_notice_cache.pop(key, None)
        # include date so the same user leaving again (new date) always triggers a notice
        notice_key = (notify_chat_id, user_id, "left", date)
        if notice_key in vc_left_notice_cache:
            return False
        vc_left_notice_cache[notice_key] = now
        return True

    async def _fetch_vc_participant_ids(self, chat_id: int) -> set[int]:
        assistant = await group_assistant(self, chat_id)
        participants = await assistant.get_participants(chat_id)
        user_ids = set()
        for participant in participants:
            user_id = getattr(participant, "user_id", None)
            if user_id:
                user_ids.add(int(user_id))
        return user_ids

    async def _send_vc_join_notice(self, notify_chat_id: int, user_id: int,
                                    date: int = 0, source: int = 0) -> None:
        if not self._remember_join_notice(notify_chat_id, user_id, date, source):
            return
        try:
            user = await app.get_users(user_id)
            mention = user.mention
        except Exception:
            mention = f"<a href='tg://user?id={user_id}'>User</a>"
        lang = await get_lang(notify_chat_id)
        _ = get_string(lang)
        text = _["call_vc_joined"].format(mention=mention, user_id=user_id)
        msg = await app.send_message(notify_chat_id, text)
        asyncio.create_task(_auto_delete(msg, 10))

    async def _send_vc_left_notice(self, notify_chat_id: int, user_id: int,
                                    date: int = 0, source: int = 0) -> None:
        if not self._remember_left_notice(notify_chat_id, user_id, date, source):
            return
        try:
            user = await app.get_users(user_id)
            mention = user.mention
        except Exception:
            mention = f"<a href='tg://user?id={user_id}'>User</a>"
        lang = await get_lang(notify_chat_id)
        _ = get_string(lang)
        text = _["call_vc_left"].format(mention=mention, user_id=user_id)
        msg = await app.send_message(notify_chat_id, text)
        asyncio.create_task(_auto_delete(msg, 10))

    async def _handle_group_call_participants_update(
        self, update: UpdateGroupCallParticipants
    ) -> None:
        call_id = int(update.call.id)
        mapping = vc_join_call_map.get(call_id)
        if not mapping:
            return
        notify_chat_id = mapping["notify_chat_id"]
        if not await get_vcnotify(notify_chat_id):
            return
        member_snapshot = vc_join_snapshots.setdefault(mapping["chat_id"], set())
        for participant in update.participants:
            user_id = self._extract_user_id_from_peer(getattr(participant, "peer", None))
            if not user_id:
                continue
            if getattr(participant, "left", False):
                if user_id in member_snapshot:
                    member_snapshot.discard(user_id)
                    if self._remember_left_event(
                        call_id, user_id,
                        int(getattr(participant, "date", 0) or 0),
                        int(getattr(participant, "source", 0) or 0),
                    ):
                        await self._send_vc_left_notice(
                            notify_chat_id, user_id,
                            int(getattr(participant, "date", 0) or 0),
                            int(getattr(participant, "source", 0) or 0),
                        )
                continue
            if not getattr(participant, "just_joined", False):
                continue
            if user_id in member_snapshot:
                continue
            if not self._remember_join_event(
                call_id, user_id,
                int(getattr(participant, "date", 0) or 0),
                int(getattr(participant, "source", 0) or 0),
            ):
                continue
            member_snapshot.add(user_id)
            await self._send_vc_join_notice(
                notify_chat_id, user_id,
                int(getattr(participant, "date", 0) or 0),
                int(getattr(participant, "source", 0) or 0),
            )

    async def _vc_join_monitor_loop(self, chat_id: int, notify_chat_id: int) -> None:
        try:
            while True:
                if not await get_vcnotify(notify_chat_id):
                    vc_join_snapshots.pop(chat_id, None)
                    await asyncio.sleep(1)
                    continue
                try:
                    current_ids = await self._fetch_vc_participant_ids(chat_id)
                except Exception:
                    await asyncio.sleep(1)
                    continue
                previous_ids = vc_join_snapshots.get(chat_id)
                if previous_ids is None:
                    vc_join_snapshots[chat_id] = current_ids
                    await asyncio.sleep(1)
                    continue
                for uid in current_ids - previous_ids:
                    try:
                        await self._send_vc_join_notice(notify_chat_id, uid)
                    except Exception:
                        pass
                for uid in previous_ids - current_ids:
                    try:
                        await self._send_vc_left_notice(notify_chat_id, uid)
                    except Exception:
                        pass
                vc_join_snapshots[chat_id] = current_ids
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            raise
        finally:
            task = vc_join_monitors.get(chat_id)
            if task is asyncio.current_task():
                vc_join_monitors.pop(chat_id, None)

    async def maybe_start_vc_join_notifier(self, chat_id: int, notify_chat_id: int) -> bool:
        if not await get_vcnotify(notify_chat_id):
            return False
        call_id = await self._resolve_vc_call_id(chat_id)
        vc_join_targets[chat_id] = notify_chat_id

        old_call_id = next(
            (k for k, v in vc_join_call_map.items() if v.get("chat_id") == chat_id), None
        )
        new_session = call_id and (old_call_id is None or old_call_id != call_id)

        if call_id:
            if old_call_id and old_call_id != call_id:
                vc_join_call_map.pop(old_call_id, None)
            vc_join_call_map[call_id] = {"chat_id": chat_id, "notify_chat_id": notify_chat_id}

        if new_session or chat_id not in vc_join_snapshots:
            try:
                vc_join_snapshots[chat_id] = await self._fetch_vc_participant_ids(chat_id)
            except Exception:
                vc_join_snapshots[chat_id] = set()

        existing = vc_join_monitors.get(chat_id)
        if not existing or existing.done():
            vc_join_monitors[chat_id] = asyncio.create_task(
                self._vc_join_monitor_loop(chat_id, notify_chat_id)
            )
        return True

    async def stop_vc_join_notifier(self, chat_id: int) -> None:
        task = vc_join_monitors.pop(chat_id, None)
        if task and not task.done():
            task.cancel()
        vc_join_snapshots.pop(chat_id, None)
        vc_join_targets.pop(chat_id, None)
        for call_id, info in list(vc_join_call_map.items()):
            if info.get("chat_id") == chat_id:
                vc_join_call_map.pop(call_id, None)

    async def ping(self):
        pings = []
        if config.STRING1:
            pings.append(await self.one.ping)
        return str(round(sum(pings) / len(pings), 3))

    async def start(self):
        LOGGER(__name__).info("Starting PyTgCalls Client...\n")
        if config.STRING1:
            await self.one.start()

    async def decorators(self):
        @self.one.on_update()
        async def stream_services_handler(client, update: Update):
            from pytgcalls.types import ChatUpdate
            if isinstance(update, ChatUpdate):
                if update.status & (
                    ChatUpdate.Status.KICKED
                    | ChatUpdate.Status.LEFT_GROUP
                    | ChatUpdate.Status.CLOSED_VOICE_CHAT
                ):
                    await self.stop_stream(update.chat_id)
            elif isinstance(update, StreamEnded):
                await self.change_stream(client, update.chat_id)

        if self.userbot1:
            async def raw_group_call_handler(client, update, users, chats) -> None:
                try:
                    if isinstance(update, UpdateGroupCallParticipants):
                        await self._handle_group_call_participants_update(update)
                    elif isinstance(update, UpdateGroupCall):
                        call = update.call
                        if "Discarded" in type(call).__name__:
                            call_id = getattr(call, "id", None)
                            if call_id:
                                mapping = vc_join_call_map.get(int(call_id))
                                if mapping:
                                    await _clear_(mapping["chat_id"])
                except Exception:
                    pass
            self.userbot1.add_handler(RawUpdateHandler(raw_group_call_handler), group=99)

Muskan = Call()