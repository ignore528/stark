# © @MuskanBot

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import config
from Muskan_Music import app
from Muskan_Music._btns import danger_button, primary_button, success_button

def start_panel(_):
    buttons = [
        [
            primary_button(
                text=_["SO_B_1"], url=f"https://t.me/{app.username}?startgroup=true", icon_custom_emoji_id=5258362837411045098),
            ),
            success_button(text=_["S_B_2"], url=config.SUPPORT_CHAT),
        ],
    ]
    return buttons

def private_panel(_):
    buttons = [
        [
            primary_button(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true", icon_custom_emoji_id=5258362837411045098),
            )
        ],
        [
            success_button(text=_["S_B_4"], callback_data="settings_back_helper", icon_custom_emoji_id=5314504236132747481),
        ],
        [
            danger_button(text=_["S_B_6"], url=config.SUPPORT_CHANNEL, icon_custom_emoji_id=5424818078833715060),
            success_button(text=_["S_B_2"], url=config.SUPPORT_CHAT, icon_custom_emoji_id=5443038326535759644),
        ],
    ]
    if config.SOURCE and config.SOURCE.startswith("http"):
        buttons.append([primary_button(text=_["S_B_7"], url=config.SOURCE)])
    return buttons
