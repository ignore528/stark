# Entry point — applies compatibility patches before any pyrogram import
import patches  # must be first

import asyncio
import sys
import os

# Add bot dir to path
sys.path.insert(0, os.path.dirname(__file__))

from Muskan_Music.__main__ import init

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
