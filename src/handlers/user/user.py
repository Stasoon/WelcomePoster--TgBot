import json
import os

import aiofiles
import asyncio
from aiogram import Dispatcher
from aiogram.types import ChatJoinRequest, Message, InputMediaPhoto

from src.database.users import create_user
from src.create_bot import bot
from config import Config

# region Utils


async def get_data_from_json(path) -> dict:
    async with aiofiles.open(path, mode='r') as file:
        contents = await file.read()
        data = json.loads(contents)
    return data


async def get_photos_list_from_file() -> tuple:
    data = await get_data_from_json(Config.Paths.WELCOME_POST_CONTENT_JSON)
    return data['images']


async def get_welcome_text_from_file() -> str:
    data = await get_data_from_json(Config.Paths.WELCOME_POST_CONTENT_JSON)
    return data['text']


async def send_welcome_post_to_user(user_id: int):
    media_group = []
    text = await get_welcome_text_from_file()
    photos = await get_photos_list_from_file()

    if len(photos) == 1:
        await bot.send_photo(chat_id=user_id, caption=text, photo=photos[0])
    elif len(photos) > 2:
        for n, img in enumerate(photos):
            media_group.append(InputMediaPhoto(media=img, caption=text if n == 0 else ''))

        await bot.send_media_group(
            chat_id=user_id,
            media=media_group
        )
    else:
        await bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode='HTML'
        )

# endregion


# region Handlers


async def handle_start_command(message: Message):
    await send_welcome_post_to_user(user_id=message.from_user.id)


async def handle_chat_join_request(chat_join: ChatJoinRequest):
    user_id = chat_join.from_user.id

    # сохраняем пользователя в БД
    create_user(
        telegram_id=user_id,
        name=chat_join.from_user.username or chat_join.from_user.full_name,
        reflink=f'{chat_join.invite_link},{chat_join.chat.title}'
    )

    delay_seconds_before_welcome = 60
    await asyncio.sleep(delay_seconds_before_welcome)

    await send_welcome_post_to_user(user_id=user_id)


# endregion


def register_user_handlers(dp: Dispatcher) -> None:
    # показать команду
    dp.register_message_handler(handle_start_command, commands=['start'])

    # обработчик запроса в канале
    dp.register_chat_join_request_handler(handle_chat_join_request)
