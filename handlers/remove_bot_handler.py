from StaticData import StaticData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from aiogram import F
import keyboards
import requests

class RemoveBotState(StatesGroup):
    selecting_bot = State()
    confirm_remove = State()

@StaticData.dp.callback_query(F.data.split(";")[0] == "remove_bot")
async def remove_bot(callback: types.CallbackQuery, state: FSMContext):
    if StaticData.logged_in(callback.message.chat.id):
        user = StaticData.get_user(callback.message.chat.id)
        if user["privilege"] in ["ADMIN", "MAIN_ADMIN"]:
            user_state = await state.get_state()
            if user_state != RemoveBotState.selecting_bot:
                data = {
                    "username": user["name"],
                    "password": user["password"]
                }
                response = requests.post("http://192.168.31.55:6000/get_all_bots", data=data)
                if response.status_code == 200:
                    result = response.json()
                    bots = [bot["name"] for bot in result]
                    await state.set_state(RemoveBotState.selecting_bot)
                    await state.update_data(bots=bots)
                    await state.update_data(callback=callback)
                    await StaticData.bot.edit_message_text(f"Выберите бота: ", 
                                        chat_id=callback.message.chat.id, 
                                        message_id=callback.message.message_id,
                                        reply_markup=get_bots_keyboard(bots, 1))
                    await callback.answer()
                else:
                    await StaticData.bot.edit_message_text(f"Упс... Что-то пошло не так...", 
                                        chat_id=callback.message.chat.id, 
                                        message_id=callback.message.message_id,
                                        reply_markup=keyboards.get_cancel_keyboard())
                await callback.answer()
            else:
                user_data = await state.get_data()
                page = int(callback.data.split(";")[1])
                await StaticData.bot.edit_message_text(f"Выберите бота: ", 
                                            chat_id=callback.message.chat.id, 
                                            message_id=callback.message.message_id,
                                            reply_markup=get_bots_keyboard(user_data["bots"], page))
                await callback.answer()
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
        await state.clear()
        await callback.answer()


@StaticData.dp.callback_query(F.data.split(";")[0] == "pick_remove_bot")
async def pick_remove_bot(callback: types.CallbackQuery, state: FSMContext):
    if callback.message.chat.id in StaticData.users.keys():
        user = StaticData.users[callback.message.chat.id]
        bot_name = callback.data.split(";")[1]
        await state.update_data(bot_name=bot_name)
        await state.set_state(RemoveBotState.confirm_remove)
        await StaticData.bot.edit_message_text(f"Для удаления бота подтвердите действие - введите название бота!", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_cancel_keyboard("Отмена"))
        await callback.answer()
    else:
        await StaticData.bot.edit_message_text(f"Для начала войдите в аккаунт!", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_login_menu())
        await state.clear()
        await callback.answer()


@StaticData.dp.message(RemoveBotState.confirm_remove)
async def confirm_remove(message: types.Message, state: FSMContext):
    user_input = message.text
    await StaticData.bot.delete_message(message.chat.id, message.message_id)
    user_data = await state.get_data()
    callback = user_data["callback"]
    bot_name = user_data["bot_name"]
    if bot_name == user_input:
        user = StaticData.get_user(callback.message.chat.id)
        data = {
            "botname": bot_name,
            "username": user["name"],
            "password": user["password"]
        }
        response = requests.post("http://192.168.31.55:6000/remove_bot", data=data)
        await StaticData.bot.edit_message_text(f"Бот {bot_name} успешно удален!", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_cancel_keyboard("Ура"))
        await state.clear()
    else:
        await StaticData.bot.edit_message_text(f"Удаление бота отменено!", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_cancel_keyboard())
        await state.clear()


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
    for i in range(first_index, min(first_index + bots_in_page, len(bots_list))):
        builder.row(types.InlineKeyboardButton(
            text=bots_list[i],
            callback_data=f"pick_remove_bot;{bots_list[i]}"
        ))
    if 1 < page < max_page:
        builder.row(
            types.InlineKeyboardButton(
                text="<",
                callback_data=f"remove_bot;{max(page-1, 1)}"
            ),
            types.InlineKeyboardButton(
                text=">",
                callback_data=f"remove_bot;{min(page+1, max_page)}"
            ),
        )
    elif max_page == 1:
        pass
    elif page == 1:
        builder.row(
            types.InlineKeyboardButton(
                text=">",
                callback_data=f"remove_bot;{min(page+1, max_page)}"
            ),
        )
    elif page == max_page:
        builder.row(
            types.InlineKeyboardButton(
                text="<",
                callback_data=f"remove_bot;{max(page-1, 1)}"
            ),
        )
    return builder.as_markup()