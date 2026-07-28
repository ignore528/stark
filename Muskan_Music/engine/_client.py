# © @MuskanBot

from pyrogram import Client, errors
from pyrogram.enums import ChatMemberStatus, ParseMode

import config

from .._logging import LOGGER

class Muskan(Client):
    def __init__(self):
        LOGGER(__name__).info(f"Starting Bot...")
        super().__init__(
            name="Muskan_Music",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            max_concurrent_transmissions=7,
        )

    async def start(self):
        await super().start()
        self.id = self.me.id
        self.name = self.me.first_name + " " + (self.me.last_name or "")
        self.username = self.me.username
        self.mention = self.me.mention

        if config.LOGGER_ID and config.LOGGER_ID != 0:
            try:
                # resolve peer first so pyrogram caches it (avoids ValueError on fresh sessions)
                await self.get_chat(config.LOGGER_ID)
                await self.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"<u><b>» {self.mention} ʙᴏᴛ sᴛᴀʀᴛᴇᴅ :</b></u>\n\nɪᴅ : <code>{self.id}</code>\nɴᴀᴍᴇ : {self.name}\nᴜsᴇʀɴᴀᴍᴇ : @{self.username}",
                    parse_mode=ParseMode.HTML,
                )
            except (errors.ChannelInvalid, errors.PeerIdInvalid, ValueError):
                LOGGER(__name__).warning(
                    "Bot could not access the log group/channel. Continuing without logger."
                )
            except Exception as ex:
                LOGGER(__name__).warning(
                    f"Log group/channel issue: {type(ex).__name__}: {ex}. Continuing anyway."
                )

            try:
                a = await self.get_chat_member(config.LOGGER_ID, self.id)
                if a.status != ChatMemberStatus.ADMINISTRATOR:
                    LOGGER(__name__).warning(
                        "Bot is not admin in log group/channel, but continuing anyway."
                    )
            except Exception:
                pass  # some log groups allow non-admin bots
        else:
            LOGGER(__name__).info("LOGGER_ID not set, skipping log channel notification.")
        LOGGER(__name__).info(f"Music Bot Started as {self.name}")

    async def stop(self):
        await super().stop()