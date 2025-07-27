from StaticData import StaticData
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram import F
import keyboards
import requests

@StaticData.dp.callback_query(F.data == "logout")
async def logout(callback: types.CallbackQuery, state: FSMContext):
    data = {
        "chatID": callback.message.chat.id
    }
    response = requests.post("http://192.168.31.55:6000/logout", data=data)
    if response.status_code == 200:
        await StaticData.bot.edit_message_text(f"Добро пожаловать в бота!", 
                                        chat_id=callback.message.chat.id, 
                                        message_id=callback.message.message_id,
                                        reply_markup=keyboards.get_login_menu())
        await state.clear()
        StaticData.users.pop(callback.message.chat.id)
        await callback.answer()
    else:
        await StaticData.bot.edit_message_text(f"Произошла ошибка!", 
                                        chat_id=callback.message.chat.id, 
                                        message_id=callback.message.message_id,
                                        reply_markup=keyboards.get_cancel_keyboard())
