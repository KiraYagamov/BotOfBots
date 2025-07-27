from StaticData import StaticData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from aiogram import F
import keyboards
import requests

@StaticData.dp.callback_query(F.data == "get_bots_list")
async def get_bots_list(callback: types.CallbackQuery, state: FSMContext):
    if StaticData.logged_in(callback.message.chat.id):
        user = StaticData.get_user(callback.message.chat.id)
        if user["privilege"] in ["ADMIN", "MAIN_ADMIN"]:
            data = {
                "username": user["name"],
                "password": user["password"]
            }
            response = requests.post("http://192.168.31.55:6000/get_all_bots", data=data)
            if response.status_code == 200:
                result = response.json()
                bots = [bot["name"] for bot in result]
                bots_list = ""
                for i in range(len(bots)):
                    bot = bots[i]
                    bots_list += "\n" + f"{i+1}) " + bot
                await StaticData.bot.edit_message_text(f"Вот список доступных ботов: {bots_list}", 
                                        chat_id=callback.message.chat.id, 
                                        message_id=callback.message.message_id,
                                        reply_markup=keyboards.get_cancel_keyboard())
                await callback.answer()
            else:
                await StaticData.bot.edit_message_text(f"Упс... Что-то пошло не так...", 
                                        chat_id=callback.message.chat.id, 
                                        message_id=callback.message.message_id,
                                        reply_markup=keyboards.get_cancel_keyboard())
    else:
        await StaticData.bot.edit_message_text(f"Для начала войдите в аккаунт!", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_login_menu())
        await state.clear()
        await callback.answer()