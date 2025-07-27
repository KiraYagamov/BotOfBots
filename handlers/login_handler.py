from StaticData import StaticData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import types
from aiogram import F
import keyboards
import requests

class LoginState(StatesGroup):
    enter_name = State()
    enter_password = State()

@StaticData.dp.callback_query(F.data == "login")
async def login(callback: types.CallbackQuery, state: FSMContext):
    await StaticData.bot.edit_message_text("Введите Ваш логин", 
                                chat_id=callback.message.chat.id, 
                                message_id=callback.message.message_id,
                                reply_markup=keyboards.get_cancel_keyboard())
    await state.set_state(LoginState.enter_name)
    await state.update_data(callback_message=callback.message)
    await callback.answer()

@StaticData.dp.message(LoginState.enter_name)
async def enter_name(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    callback_message = user_data["callback_message"]
    await state.update_data(user_login=message.text)
    await StaticData.bot.delete_message(message.chat.id, message.message_id)
    await StaticData.bot.edit_message_text(f"Отлично! Теперь введите Ваш пароль", 
                                chat_id=callback_message.chat.id, 
                                message_id=callback_message.message_id,
                                reply_markup=keyboards.get_cancel_keyboard())
    await state.set_state(LoginState.enter_password)

@StaticData.dp.message(LoginState.enter_password)
async def enter_name(message: types.Message, state: FSMContext):
    await state.update_data(user_password=message.text)
    user_data = await state.get_data()
    callback_message = user_data["callback_message"]
    await StaticData.bot.delete_message(message.chat.id, message.message_id)
    user_data = await state.get_data()
    data = {
        "username": user_data["user_login"],
        "password": user_data["user_password"],
        "chatID": message.chat.id
    }
    response = requests.post("http://192.168.31.55:6000/login", data=data)

    if response.status_code == 200:
        await StaticData.bot.edit_message_text(
            f"Вы успешно вошли в аккаунт!", 
                                    chat_id=callback_message.chat.id, 
                                    message_id=callback_message.message_id,
                                    reply_markup=keyboards.get_cancel_keyboard(text="Понятно"))
        StaticData.users[message.chat.id] = response.json()
    else:
        await StaticData.bot.edit_message_text(
            f"Произошла ошибка при входе в аккаунт. " + \
            "Убедитесь, что Вы правильно вводите Ваши логин и пароль!", 
                                    chat_id=callback_message.chat.id, 
                                    message_id=callback_message.message_id,
                                    reply_markup=keyboards.get_cancel_keyboard())
    await state.clear()
