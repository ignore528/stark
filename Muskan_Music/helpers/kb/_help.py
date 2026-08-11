# © @MuskanBot

from typing import Union
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from Muskan_Music import app
from Muskan_Music._btns import danger_button, primary_button, success_button

def help_pannel(_, START: Union[bool, int] = None):
    first = [danger_button(text=_["CLOSE_BUTTON"], callback_data="close")]
    second = [
        primary_button(
            text=_["BACK_BUTTON"],
            callback_data="go_to_start",
        ),
    ]
    mark = second if START else first

    upl = InlineKeyboardMarkup(
        [
            [
                primary_button(text=_["H_B_1"], callback_data="h:1", icon_custom_emoji_id=6269458311381258421),
                success_button(text=_["H_B_3"], callback_data="h:3", icon_custom_emoji_id=5424818078833715060),
            ],
            [
                danger_button(text=_["H_B_6"], callback_data="h:6", icon_custom_emoji_id=5208607440878197365),
                primary_button(text=_["H_B_7"], callback_data="h:7", icon_custom_emoji_id=5420323339723881652),
            ],
            [
                success_button(text=_["H_B_10"], callback_data="h:10", icon_custom_emoji_id=5269563867305879894),
                danger_button(text=_["H_B_11"], callback_data="h:11", icon_custom_emoji_id=5463107823946717464),
            ],
            [
                primary_button(text=_["H_B_12"], callback_data="h:12", icon_custom_emoji_id=5294339927318739359),
                success_button(text=_["H_B_13"], callback_data="h:13", icon_custom_emoji_id=6269085886177087845),
            ],
            [
                danger_button(text=_["H_B_15"], callback_data="h:15", icon_custom_emoji_id=5456140674028019486),
            ],
            mark,
        ]
    )
    return upl

def help_back_markup(_):
    upl = InlineKeyboardMarkup(
        [
            [
                primary_button(
                    text=_["BACK_BUTTON"], 
                    callback_data="settings_back_helper",
                    icon_custom_emoji_id=5816895683256390576),
                ),
            ]
        ]
    )
    return upl

def private_help_panel(_):
    buttons = [
        [
            success_button(
                text=_["S_B_4"],
                url=f"https://t.me/{app.username}?start=help", 
            ),
        ],
    ]
    return buttons
