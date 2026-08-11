# © @MuskanBot

from typing import Union

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from Muskan_Music._btns import danger_button, primary_button, success_button

def queue_markup(_, DURATION, CPLAY, videoid, played: Union[bool, int] = None, dur: Union[bool, int] = None):
    not_dur = [
        [
            primary_button(
                text=_["QU_B_1"],
                callback_data=f"GetQueued {CPLAY}|{videoid}",
            ),
            danger_button(
                text=_["CLOSE_BUTTON"],
                callback_data="close", icon_custom_emoji_id=5445267414562389170)],
            ),
        ]
    ]
    with_dur = [
        [
            InlineKeyboardButton(
                text=_["QU_B_2"].format(played, dur),
                callback_data="GetTimer",
            )
        ],
        [
            primary_button(
                text=_["QU_B_1"],
                callback_data=f"GetQueued {CPLAY}|{videoid}",
            ),
            danger_button(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
            ),
        ],
    ]
    upl = InlineKeyboardMarkup(not_dur if DURATION == "Unknown" else with_dur)
    return upl

def queue_back_markup(_, CPLAY):
    upl = InlineKeyboardMarkup(
        [
            [
                primary_button(
                    text=_["BACK_BUTTON"],
                    callback_data=f"queue_back_timer {CPLAY}",
                ),
                danger_button(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
                ),
            ]
        ]
    )
    return upl

def aq_markup(_, chat_id):
    buttons = [
        [
            danger_button(text=_["CLOSE_BUTTON"], callback_data="close"),
        ]
    ]
    return buttons
