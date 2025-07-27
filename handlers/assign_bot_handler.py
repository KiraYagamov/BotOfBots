from StaticData import StaticData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from aiogram import F
import keyboards
import requests

class AssignBotState(StatesGroup):
    selecting_user = State()
    selecting_bot = State()

@StaticData.dp.callback_query(F.data.split(";")[0] == "assign_bot")
async def assign_bot(callback: types.CallbackQuery, state: FSMContext):
    if StaticData.logged_in(callback.message.chat.id):
        user = StaticData.users[callback.message.chat.id]
        if user["privilege"] in ["ADMIN", "MAIN_ADMIN"]:
            await state.set_state(AssignBotState.selecting_user)
            await state.update_data(callback=callback)
            await StaticData.bot.edit_message_text(f"Введите имя пользователя", 
                                        chat_id=callback.message.chat.id, 
                                        message_id=callback.message.message_id,
                                        reply_markup=keyboards.get_cancel_keyboard())
        else:
            await StaticData.bot.edit_message_text(f"У Вас нет доступа к этой команде!", 
                                        chat_id=callback.message.chat.id, 
                                        message_id=callback.message.message_id,
                                        reply_markup=keyboards.get_cancel_keyboard("Блин :("))
        await callback.answer()
    else:
        await StaticData.bot.edit_message_text(f"Для начала войдите в аккаунт!", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_login_menu())
        await state.clear()
        await callback.answer()

@StaticData.dp.message(AssignBotState.selecting_user)
async def selecting_user(message: types.Message, state: FSMContext):
    if StaticData.logged_in(message.chat.id):
        user_data = await state.get_data()
        callback = user_data["callback"]
        user = StaticData.users[message.chat.id]
        assign_username = message.text
        await StaticData.bot.delete_message(message.chat.id, message.message_id)
        await state.update_data(assign_username=assign_username)
        await state.set_state(AssignBotState.selecting_bot)
        bots_list = get_bots_list(user)
        if bots_list == -1:
            await StaticData.bot.edit_message_text(f"Упс... Что-то пошло не так...", 
                                        chat_id=callback.message.chat.id, 
                                        message_id=callback.message.message_id,
                                        reply_markup=keyboards.get_cancel_keyboard())
            await state.clear()
            return
        await StaticData.bot.edit_message_text(f"Выберите бота из списка или введите его имя", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=get_bots_keyboard(bots_list=bots_list, page=1))
    else:
        await StaticData.bot.edit_message_text(f"Для начала войдите в аккаунт!", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_login_menu())
        await state.clear()

@StaticData.dp.callback_query(F.data.split(";")[0] == "load_assign_page")
async def load_assign_page(callback: types.CallbackQuery, state: FSMContext):
    user = StaticData.users[callback.message.chat.id]
    bots_list = get_bots_list(user)
    if bots_list == -1:
            await StaticData.bot.edit_message_text(f"Упс... Что-то пошло не так...", 
                                        chat_id=callback.message.chat.id, 
                                        message_id=callback.message.message_id,
                                        reply_markup=keyboards.get_cancel_keyboard())
            await state.clear()
            await callback.answer()
            return
    page = int(callback.data.split(";")[1])
    await StaticData.bot.edit_message_text(f"Выберите бота: ", 
                                        chat_id=callback.message.chat.id, 
                                        message_id=callback.message.message_id,
                                        reply_markup=get_bots_keyboard(bots_list, page))
    await callback.answer()


@StaticData.dp.callback_query(F.data.split(";")[0] == "pick_assign_bot")
async def pick_assign_bot(callback: types.CallbackQuery, state: FSMContext):
    if StaticData.logged_in(callback.message.chat.id):
        user = StaticData.users[callback.message.chat.id]
        user_data = await state.get_data()
        bot_name = callback.data.split(";")[1]
        data = {
            "username": user["name"],
            "password": user["password"],
            "givinguser": user_data["assign_username"],
            "botname": bot_name
        }
        response = requests.post("http://192.168.31.55:6000/give_access", data=data)
        if response.status_code == 200:
            await StaticData.bot.edit_message_text(f"Бот {bot_name} успешно присвоен пользователю {user_data["assign_username"]}!", 
                                        chat_id=callback.message.chat.id, 
                                        message_id=callback.message.message_id,
                                        reply_markup=keyboards.get_cancel_keyboard("Понятно"))
        else:
            await StaticData.bot.edit_message_text(f"Что-то пошло не так...", 
                                        chat_id=callback.message.chat.id, 
                                        message_id=callback.message.message_id,
                                        reply_markup=keyboards.get_cancel_keyboard("Жаль"))
        await state.clear()
        await callback.answer()
    else:
        await StaticData.bot.edit_message_text(f"Для начала войдите в аккаунт!", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_login_menu())
        await state.clear()
        await callback.answer()

def get_bots_list(user):
    data = {
        "username": user["name"],
        "password": user["password"]
    }
    response = requests.post("http://192.168.31.55:6000/get_all_bots", data=data)
    if response.status_code == 200:
        result = response.json()
        bots = [bot["name"] for bot in result]
        return bots
    else:
        return -1

def get_bots_keyboard(bots_list, page):
    bots_in_page = 5
    builder = InlineKeyboardBuilder()
    first_index = (page-1) * bots_in_page
    max_page = len(bots_list) // bots_in_page
    if len(bots_list) > max_page * bots_in_page:
        max_page += 1

    builder.row(types.InlineKeyboardButton(
        text="Назад",
        callback_data=f"cancel"
    ))
    if max_page == 0:
        return builder.as_markup()
    for i in range(first_index, min(first_index + bots_in_page, len(bots_list))):
        builder.row(types.InlineKeyboardButton(
            text=bots_list[i],
            callback_data=f"pick_assign_bot;{bots_list[i]}"
        ))
    if 1 < page < max_page:
        builder.row(
            types.InlineKeyboardButton(
                text="<",
                callback_data=f"load_assign_page;{max(page-1, 1)}"
            ),
            types.InlineKeyboardButton(
                text=">",
                callback_data=f"load_assign_page;{min(page+1, max_page)}"
            ),
        )
    elif max_page == 1:
        pass
    elif page == 1:
        builder.row(
            types.InlineKeyboardButton(
                text=">",
                callback_data=f"load_assign_page;{min(page+1, max_page)}"
            ),
        )
    elif page == max_page:
        builder.row(
            types.InlineKeyboardButton(
                text="<",
                callback_data=f"load_assign_page;{max(page-1, 1)}"
            ),
        )
    return builder.as_markup()