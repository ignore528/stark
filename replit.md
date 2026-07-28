# Muskan Music Bot

A powerful Telegram music bot that streams high-quality audio & video in Telegram voice chats from YouTube, Spotify, Apple Music, SoundCloud, Resso, and more.

## Run

```
pip install -r requirements.txt
python3 run.py
```

## Required Environment Variables

Set these as Replit Secrets before running:

| Variable | Description |
|---|---|
| `API_ID` | Telegram API ID from my.telegram.org |
| `API_HASH` | Telegram API Hash from my.telegram.org |
| `BOT_TOKEN` | Bot token from @BotFather |
| `OWNER_ID` | Your Telegram user ID |
| `LOGGER_ID` | Log group/channel ID |
| `MONGO_DB_URI` | MongoDB connection string |
| `STRING_SESSION` | Pyrogram string session for assistant |

## Optional Variables

See `sample.env` for all optional variables like `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `STRING_SESSION2`–`STRING_SESSION5`, etc.

## Stack

- Python 3.11
- Pyrogram (Kurigram fork) — Telegram MTProto client
- py-tgcalls — Voice/video call support
- MongoDB (Motor) — Database
- yt-dlp — YouTube downloading
- Pillow — Thumbnail generation

## User preferences

_Populate as needed._
