from StaticData import StaticData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from aiogram import F
import keyboards
import requests

class CreateBotState(StatesGroup):
    selecting_name = State()
    selecting_password = State()
    selecting_lang = State()

@StaticData.dp.callback_query(F.data == "create_bot")
async def create_bot(callback: types.CallbackQuery, state: FSMContext):
    if StaticData.logged_in(callback.message.chat.id):
        user = StaticData.get_user(callback.message.chat.id)
        if user["privilege"] in ["ADMIN", "MAIN_ADMIN"]:
            await state.set_state(CreateBotState.selecting_name)
            await state.update_data(user=user)
            await state.update_data(callback=callback)
            await StaticData.bot.edit_message_text(f"Введите имя бота", 
                                        chat_id=callback.message.chat.id, 
                                        message_id=callback.message.message_id,
                                        reply_markup=keyboards.get_cancel_keyboard())
        else:
            await StaticData.bot.edit_message_text(f"У Вас нет доступа к этой команде!", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_cancel_keyboard("Жаль"))
    else:
        await StaticData.bot.edit_message_text(f"Для начала войдите в аккаунт!", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_login_menu())

@StaticData.dp.message(CreateBotState.selecting_name)
async def selecting_name(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    callback = user_data["callback"]
    bot_name = message.text
    await StaticData.bot.delete_message(message.chat.id, message.message_id)
    await state.update_data(bot_name=bot_name)
    await state.set_state(CreateBotState.selecting_password)
    await StaticData.bot.edit_message_text(f"Введите пароль бота", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_cancel_keyboard())

@StaticData.dp.message(CreateBotState.selecting_password)
async def selecting_password(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    callback = user_data["callback"]
    bot_password = message.text
    await StaticData.bot.delete_message(message.chat.id, message.message_id)
    await state.update_data(bot_password=bot_password)
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="Python",
            callback_data="select_lang;py"
        )
    )
    await StaticData.bot.edit_message_text(f"Выберите язык", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=builder.as_markup())

@StaticData.dp.callback_query(F.data.split(";")[0] == "select_lang")
async def select_lang(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    user = user_data["user"]
    bot_name = user_data["bot_name"]
    bot_password = user_data["bot_password"]
    bot_lang = callback.data.split(";")[1]
    await state.update_data(bot_lang=bot_lang)
    await StaticData.bot.edit_message_text(f"Создаем Вашего бота...", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_cancel_keyboard("Понятно"))
    data = {
        "username": user["name"],
        "password": user["password"],
        "botname": bot_name,
        "botpassword": bot_password,
        "lang": bot_lang
    }
    response = requests.post("http://192.168.31.55:6000/create_bot", data=data)
    if response.status_code == 200:
        await StaticData.bot.edit_message_text(f"Ваш бот успешно создан!", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_cancel_keyboard("Понятно"))
    else:
        await StaticData.bot.edit_message_text(f"Произошла ошибка при создании бота: {response.text}", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_cancel_keyboard("Понятно"))
    
