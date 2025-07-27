from StaticData import StaticData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from aiogram import F
import keyboards
import requests


@StaticData.dp.callback_query(F.data == "ok")
async def ok(callback: types.CallbackQuery, state: FSMContext):
    await StaticData.bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await state.clear()
    await callback.answer()
