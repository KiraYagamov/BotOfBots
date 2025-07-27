from StaticData import StaticData
import asyncio
import logging
from aiogram import types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from handlers import *

logging.basicConfig(level=logging.INFO)

@StaticData.dp.message(Command("start"))
async def start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="Войти",
        callback_data="login"
    ))
    await message.answer(
        "Добро пожаловать в бота!",
        reply_markup=builder.as_markup()
    )
    await StaticData.bot.delete_message(message.chat.id, message.message_id)

async def main():
    StaticData.load_logged_in_users()
    await StaticData.dp.start_polling(StaticData.bot)

if __name__ == "__main__":
    asyncio.run(main())
