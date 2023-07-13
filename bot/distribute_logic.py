import asyncio
from aiogram import types
from aiogram.utils.exceptions import RetryAfter, MessageNotModified
from config_pr import bot
import random
from bot.decorators import send_limited

i = [i for i in range(4, 16)]


@send_limited()
async def send_message_async(chat_id, message, keyboard):
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            reply_markup=keyboard
        )
    except RetryAfter as e:
        await asyncio.sleep(e.timeout)
        return await send_message_async(chat_id, message, keyboard)
    except Exception:
        return 1


async def send_message_admin(admin, info):
    try:
        await asyncio.sleep(random.choice(i))
        await bot.send_message(admin, info, parse_mode='HTML')
    except RetryAfter as e:
        await asyncio.sleep(e.timeout)
        return await send_message_admin(admin, info)
    except Exception:
        return


async def delete_button(call: types.CallbackQuery):
    try:
        await bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=None
        )
    except MessageNotModified:
        pass
    except RetryAfter as e:
        await asyncio.sleep(e.timeout)
        return await delete_button(call)


async def bot_send_message(user_id, text, reply_markup=None):
    try:
        await bot.send_message(user_id, text, reply_markup=reply_markup)
    except RetryAfter as e:
        await asyncio.sleep(e.timeout)
        return await bot_send_message(user_id, text, reply_markup)
    except Exception:
        return
