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
                primary_button(text=_["H_B_1"], callback_data="h:1"),
                success_button(text=_["H_B_3"], callback_data="h:3"),
            ],
            [
                danger_button(text=_["H_B_6"], callback_data="h:6"),
                primary_button(text=_["H_B_7"], callback_data="h:7"),
            ],
            [
                success_button(text=_["H_B_10"], callback_data="h:10"),
                danger_button(text=_["H_B_11"], callback_data="h:11"),
            ],
            [
                primary_button(text=_["H_B_12"], callback_data="h:12"),
                success_button(text=_["H_B_13"], callback_data="h:13"),
            ],
            [
                danger_button(text=_["H_B_15"], callback_data="h:15"),
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
