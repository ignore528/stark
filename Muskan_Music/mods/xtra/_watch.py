# © @MuskanBot

from pyrogram import filters
from pyrogram.types import Message

from Muskan_Music import app
from Muskan_Music.engine._vclient import Muskan

welcome = 20
close = 30

@app.on_message(filters.video_chat_started, group=welcome)
@app.on_message(filters.video_chat_ended, group=close)
async def welcome(_, message: Message):
    await Muskan.stop_stream_force(message.chat.id)