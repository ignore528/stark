# © @MuskanBot

import asyncio
import os
import re
import json
from typing import Union
import requests
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch
try:
    from py_yt import Recommendations as _PyYtRec
except ImportError:
    _PyYtRec = None
from Muskan_Music.helpers._store import is_on_off
from Muskan_Music.helpers._fmt import time_to_seconds
import os
import glob
import random
import logging
import aiohttp
import config
from config import LOGGER_ID
from Muskan_Music import app
from config import BASE_URL, API_KEY
from urllib.parse import urlparse, unquote

STREAM_MODE = False

def safe_yt_shell(url: str) -> bool:
    try:
        p = urlparse(url)
        if p.scheme not in ("http", "https"):
            return False
        allowed = (
            "youtube.com",
            "www.youtube.com",
            "m.youtube.com",
            "youtu.be",
        )
        if not any(domain in p.netloc for domain in allowed):
            return False
        if any(x in url for x in [";", "|", "$", "`", "\n", "\r"]):
            return False
        return True
    except Exception:
        return False

def cookie_txt_file():
    cookie_dir = f"{os.getcwd()}/cookies"
    if not os.path.exists(cookie_dir):
        return None
    cookies_files = [f for f in os.listdir(cookie_dir) if f.endswith(".txt")]
    if not cookies_files:
        return None
    cookie_file = os.path.join(cookie_dir, random.choice(cookies_files))
    return cookie_file

async def _animated_progress(mystic, label: str, done_event: asyncio.Event):
    """No-op: progress shown only in inline button, not in caption."""
    await done_event.wait()

async def _download_media(link: str, kind: str, exts: list[str], wait: int = 60, mystic=None):
    vid = link.split("v=")[-1].split("&")[0]
    os.makedirs("downloads", exist_ok=True)
    label = "⬇️ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ sᴏɴɢ..." if kind == "song" else "⬇️ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴠɪᴅᴇᴏ..."

    done_event = asyncio.Event()
    progress_task = None
    if mystic:
        progress_task = asyncio.create_task(_animated_progress(mystic, label, done_event))

    try:
        if not STREAM_MODE:
            for e in exts:
                p = f"downloads/{vid}.{e}"
                if os.path.exists(p):
                    done_event.set()
                    if progress_task:
                        try: await progress_task
                        except Exception: pass
                    return p
        async with aiohttp.ClientSession() as s:
            url = (
                f"{BASE_URL}/api/{kind}?query={vid}&api={API_KEY}"
                if STREAM_MODE
                else f"{BASE_URL}/api/{kind}?query={vid}&download=true&api={API_KEY}"
            )
            async with s.get(url) as r:
                j = await r.json()
            u = j.get("stream")
            if not u:
                raise Exception("no stream")
            if j.get("type") == "live":
                done_event.set()
                if progress_task:
                    try: await progress_task
                    except Exception: pass
                return u
            for _ in range(wait):
                async with s.get(u) as r:
                    if r.status in (200, 206):
                        break
                    if r.status in (204, 423, 404, 410):
                        await asyncio.sleep(2)
                        continue
                    if r.status in (401, 403, 429):
                        raise Exception(f"block {r.status}")
                    raise Exception(f"fail {r.status}")
            else:
                raise Exception("timeout")
            if STREAM_MODE:
                done_event.set()
                if progress_task:
                    try: await progress_task
                    except Exception: pass
                return u
            p = f"downloads/{vid}.{'mp3' if kind=='song' else 'mp4'}"
            proc = await asyncio.create_subprocess_shell(
                f'curl -L "{u}" -o "{p}" -s --max-time 120'
            )
            await proc.communicate()
            if not os.path.exists(p) or os.path.getsize(p) < 50000:
                raise Exception("dl fail")
            done_event.set()
            if progress_task:
                try: await progress_task
                except Exception: pass
            return p
    except Exception as e:
        done_event.set()
        if progress_task:
            try: await progress_task
            except Exception: pass
        await app.send_message(
            LOGGER_ID,
            f"❌ {kind.upper()} ERR\n🔗 `{link}`\n⚠️ `{str(e)[:100]}`"
        )
        raise

async def download_song(link: str, mystic=None):
    return await _download_media(link, "song", ["mp3", "m4a", "webm"], 60, mystic=mystic)

async def download_video(link: str, mystic=None):
    return await _download_media(link, "video", ["mp4", "webm", "mkv"], 90, mystic=mystic)
    

async def check_file_size(link):
    if not safe_yt_shell(link):
        return None

    async def get_format_info(link):
        cookie_file = cookie_txt_file()
        if not cookie_file:
            print("No cookies found. Cannot check file size.")
            return None
            
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--cookies", cookie_file,
            "-J",
            link,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            print(f'Error:\n{stderr.decode()}')
            return None
        return json.loads(stdout.decode())

    def parse_size(formats):
        total_size = 0
        for format in formats:
            if 'filesize' in format:
                total_size += format['filesize']
        return total_size

    info = await get_format_info(link)
    if info is None:
        return None
    
    formats = info.get('formats', [])
    if not formats:
        print("No formats found.")
        return None
    
    total_size = parse_size(formats)
    return total_size

async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if re.search(self.regex, link):
            return True
        else:
            return False

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset in (None,):
            return None
        return text[offset : offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            if str(duration_min) == "None":
                duration_sec = 0
            else:
                duration_sec = int(time_to_seconds(duration_min))
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
        return title

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            duration = result["duration"]
        return duration

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        return thumbnail

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        if not safe_yt_shell(link):
            return 0, "Invalid or unsafe URL."
        try:
            downloaded_file = await download_video(link)
            if downloaded_file:
                return 1, downloaded_file
        except Exception as e:
            print(f"Video API failed: {e}")
        
        cookie_file = cookie_txt_file()
        if not cookie_file:
            return 0, "No cookies found. Cannot download video."
            
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--cookies", cookie_file,
            "-g",
            "-f",
            "best[height<=?720][width<=?1280]",
            link,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stdout:
            return 1, stdout.decode().split("\n")[0]
        else:
            return 0, stderr.decode()

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        
        if not safe_yt_shell(link):
            return []
            
        cookie_file = cookie_txt_file()
        
        args = ["yt-dlp", "-i", "--get-id", "--flat-playlist"]
        if cookie_file:
            args.extend(["--cookies", cookie_file])
        args.extend(["--playlist-end", str(limit), "--skip-download", link])

        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        playlist_data = stdout.decode("utf-8")
        
        try:
            result = playlist_data.split("\n")
            result = [key for key in result if key.strip() != ""]
        except:
            result = []
        return result

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        results = VideosSearch(link, limit=1)

        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            vidid = result["id"]
            yturl = result["link"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]

        clean_title = title.strip()
        if len(clean_title) > 14:
            clean_title = clean_title[:14].rstrip() + "...."

        track_details = {
            "title": clean_title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }

        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        if not safe_yt_shell(link):
            return [], link

        cookie_file = cookie_txt_file()
        if not cookie_file:
            return [], link
            
        ytdl_opts = {"quiet": True, "cookiefile" : cookie_file}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r["formats"]:
                try:
                    str(format["format"])
                except:
                    continue
                if not "dash" in str(format["format"]).lower():
                    try:
                        format["format"]
                        format["filesize"]
                        format["format_id"]
                        format["ext"]
                        format["format_note"]
                    except:
                        continue
                    formats_available.append(
                        {
                            "format": format["format"],
                            "filesize": format["filesize"],
                            "format_id": format["format_id"],
                            "ext": format["ext"],
                            "format_note": format["format_note"],
                            "yturl": link,
                        }
                    )
        return formats_available, link

    async def slider(
        self,
        link: str,
        query_type: int,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid:
            link = self.base + link
            
        if not safe_yt_shell(link):
            return None, None

        loop = asyncio.get_running_loop()
        def audio_dl():
            cookie_file = cookie_txt_file()
            if not cookie_file:
                raise Exception("No cookies found. Cannot download audio.")
                
            ydl_optssx = {
                "format": "bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "cookiefile" : cookie_file,
                "no_warnings": True,
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            info = x.extract_info(link, False)
            xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            if os.path.exists(xyz):
                return xyz
            x.download([link])
            return xyz

        def video_dl():
            cookie_file = cookie_txt_file()
            if not cookie_file:
                raise Exception("No cookies found. Cannot download video.")
                
            ydl_optssx = {
                "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "cookiefile" : cookie_file,
                "no_warnings": True,
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            info = x.extract_info(link, False)
            xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            if os.path.exists(xyz):
                return xyz
            x.download([link])
            return xyz
        if songvideo or songaudio:
            await download_song(link, mystic=mystic)
            vid_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link.split("/")[-1]
            fpath = f"downloads/{vid_id}.mp3"
            return fpath
        elif video:
            try:
                downloaded_file = await download_video(link, mystic=mystic)
                if downloaded_file:
                    return downloaded_file, True
            except Exception as e:
                print(f"Video API failed: {e}")
            
            cookie_file = cookie_txt_file()
            if not cookie_file:
                return None, None
                
            if await is_on_off(1):
                direct = True
                downloaded_file = await download_song(link, mystic=mystic)
            else:
                proc = await asyncio.create_subprocess_exec(
                    "yt-dlp",
                    "--cookies", cookie_file,
                    "-g",
                    "-f",
                    "best[height<=?720][width<=?1280]",
                    link,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await proc.communicate()
                if stdout:
                    downloaded_file = stdout.decode().split("\n")[0]
                    direct = False
                else:
                    file_size = await check_file_size(link)
                    if not file_size:
                        return None, None
                    total_size_mb = file_size / (1024 * 1024)
                    if total_size_mb > 250:
                        return None, None
                    direct = True
                    downloaded_file = await loop.run_in_executor(None, video_dl)
        else:
            direct = True
            downloaded_file = await download_song(link, mystic=mystic)
        return downloaded_file, direct

    # ── AutoPlay ────────────────────────────────────────────────────────────

    @staticmethod
    def _clean_ap_title(title: str) -> str:
        title = re.sub(r"\[[^\]]*\]|\([^\)]*\)", " ", title or "")
        title = re.sub(
            r"\b(official|video|audio|lyrics?|lyrical|remix|status|song|songs|"
            r"music|feat\.?|ft\.?|prod\.?|full|hd|4k|hq|visualizer|slowed|reverb)\b",
            " ",
            title,
            flags=re.IGNORECASE,
        )
        return re.sub(r"\s+", " ", title).strip()[:80]

    @staticmethod
    def _is_ok_result(item: dict, excluded: set, max_sec: int = 7200) -> bool:
        vid = item.get("id")
        dur = item.get("duration")
        title = item.get("title")
        if not vid or not dur or not title or vid in excluded:
            return False
        try:
            from Muskan_Music.helpers._fmt import time_to_seconds as _tts
            sec = int(_tts(str(dur)))
        except Exception:
            return False
        return 30 < sec <= max_sec

    async def autoplay(
        self,
        videoid: str,
        title: str = "",
        exclude_ids: set = None,
    ):
        """Return a related YouTube track dict for autoplay, or None."""
        excluded = set(exclude_ids) if exclude_ids else set()
        excluded.add(videoid)

        def _make_result(item: dict):
            vid = item.get("id")
            dur = item.get("duration")
            t   = item.get("title", "")
            try:
                from Muskan_Music.helpers._fmt import time_to_seconds as _tts
                sec = int(_tts(str(dur)))
            except Exception:
                sec = 0
            views   = (item.get("viewCount") or {}).get("short", "Unknown views")
            channel = (item.get("channel") or {}).get("name", "YouTube")
            return {"title": t, "duration_min": dur, "duration_sec": sec,
                    "vidid": vid, "views": views, "channel": channel}

        loop = asyncio.get_event_loop()

        # ── Strategy 1: YouTube native related (Recommendations) ──────────
        if _PyYtRec is not None:
            try:
                rec = _PyYtRec(videoid)
                data = await asyncio.wait_for(
                    loop.run_in_executor(None, rec.getNextResults), timeout=8.0
                )
                for item in (data.get("result") or []):
                    if self._is_ok_result(item, excluded):
                        return _make_result(item)
            except Exception:
                pass

        # ── Strategy 2: Title-based search fallback ───────────────────────
        clean = self._clean_ap_title(title)
        query = f"{clean} song" if clean else "trending hindi songs"
        try:
            res  = VideosSearch(query, limit=20)
            data = await asyncio.wait_for(res.next(), timeout=10.0)
            for item in (data.get("result") or []):
                if self._is_ok_result(item, excluded):
                    return _make_result(item)
        except Exception:
            pass

        return None
