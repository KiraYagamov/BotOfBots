from StaticData import StaticData
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram import F
import keyboards
import requests

@StaticData.dp.callback_query(F.data == "open_admin_panel")
async def open_admin_panel(callback: types.CallbackQuery, state: FSMContext):
    if StaticData.logged_in(callback.message.chat.id):
        user = StaticData.users[callback.message.chat.id]
        data = {
            "username": user["name"],
            "password": user["password"]
        }
        response = requests.post("http://192.168.31.55:6000/check_user_privileges", data=data)
        if response.text == "admin":
            await StaticData.bot.edit_message_text(f"Добро пожаловать в админ-панель, {user["name"]}!", 
                                        chat_id=callback.message.chat.id, 
                                        message_id=callback.message.message_id,
                                        reply_markup=keyboards.get_admin_menu())
        else:
            await StaticData.bot.edit_message_text(f"У Вас нет доступа к этой команде!", 
                                        chat_id=callback.message.chat.id, 
                                        message_id=callback.message.message_id,
                                        reply_markup=keyboards.get_cancel_keyboard(text="Жаль"))
    else:
        await StaticData.bot.edit_message_text(f"Для начала войдите в аккаунт!", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_login_menu())
    await state.clear()
    await callback.answer()
