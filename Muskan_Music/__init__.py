# © @MuskanBot

from Muskan_Music.engine._client import Muskan
from Muskan_Music.engine._path import dirr
from Muskan_Music.engine._gitops import git
from Muskan_Music.engine._ubot import Userbot
from Muskan_Music.misc import dbb, heroku
from pyrogram import Client
from SafoneAPI import SafoneAPI
from ._logging import LOGGER

dirr()
git()
dbb()
heroku()

app = Muskan()
api = SafoneAPI()
userbot = Userbot()

from .srcs import *

Apple = AppleAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
