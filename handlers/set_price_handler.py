from StaticData import StaticData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from aiogram import F
import keyboards
import requests

class SetPriceState(StatesGroup):
    selecting_bot = State()
    setting_price = State()

@StaticData.dp.callback_query(F.data == "set_price")
async def set_price(callback: types.CallbackQuery, state: FSMContext):
    if StaticData.logged_in(callback.message.chat.id):
        user = StaticData.users[callback.message.chat.id]
        if user["privilege"] in ["ADMIN", "MAIN_ADMIN"]:
            await state.set_state(SetPriceState.selecting_bot)
            await state.update_data(callback=callback)
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

@StaticData.dp.callback_query(F.data.split(";")[0] == "load_set_price_page")
async def load_set_price_page(callback: types.CallbackQuery, state: FSMContext):
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

@StaticData.dp.callback_query(F.data.split(";")[0] == "pick_set_price_bot")
async def pick_set_price_bot(callback: types.CallbackQuery, state: FSMContext):
    if StaticData.logged_in(callback.message.chat.id):
        user = StaticData.users[callback.message.chat.id]
        user_data = await state.get_data()
        bot_name = callback.data.split(";")[1]
        await state.update_data(bot_name=bot_name)
        await state.set_state(SetPriceState.setting_price)
        callback = user_data["callback"]
        await StaticData.bot.edit_message_text(f"Введите новую цену бота!", 
                                        chat_id=callback.message.chat.id, 
                                        message_id=callback.message.message_id,
                                        reply_markup=keyboards.get_cancel_keyboard())

@StaticData.dp.message(SetPriceState.setting_price)
async def setting_price(message: types.Message, state: FSMContext):
    user = StaticData.users[message.chat.id]
    user_data = await state.get_data()
    callback = user_data["callback"]
    bot_name = user_data["bot_name"]
    try:
        price = int(message.text)
        await StaticData.bot.delete_message(message.chat.id, message.message_id)
    except:
        await StaticData.bot.edit_message_text(f"Введена некорректная цена!", 
                                        chat_id=callback.message.chat.id, 
                                        message_id=callback.message.message_id,
                                        reply_markup=keyboards.get_cancel_keyboard())
        await StaticData.bot.delete_message(message.chat.id, message.message_id)
        return
    if StaticData.logged_in(message.chat.id):
        data = {
            "username": user["name"],
            "password": user["password"],
            "price": price,
            "botname": bot_name
        }
        response = requests.post("http://192.168.31.55:6000/set_price", data=data)
        if response.status_code == 200:
            await StaticData.bot.edit_message_text(f"Новая цена успешно установлена!", 
                                        chat_id=callback.message.chat.id, 
                                        message_id=callback.message.message_id,
                                        reply_markup=keyboards.get_cancel_keyboard())
        else:
            await StaticData.bot.edit_message_text(f"Произошла ошибка при установке цены!", 
                                        chat_id=callback.message.chat.id, 
                                        message_id=callback.message.message_id,
                                        reply_markup=keyboards.get_cancel_keyboard())
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
            callback_data=f"pick_set_price_bot;{bots_list[i]}"
        ))
    if 1 < page < max_page:
        builder.row(
            types.InlineKeyboardButton(
                text="<",
                callback_data=f"load_set_price_page;{max(page-1, 1)}"
            ),
            types.InlineKeyboardButton(
                text=">",
                callback_data=f"load_set_price_page;{min(page+1, max_page)}"
            ),
        )
    elif max_page == 1:
        pass
    elif page == 1:
        builder.row(
            types.InlineKeyboardButton(
                text=">",
                callback_data=f"load_set_price_page;{min(page+1, max_page)}"
            ),
        )
    elif page == max_page:
        builder.row(
            types.InlineKeyboardButton(
                text="<",
                callback_data=f"load_set_price_page;{max(page-1, 1)}"
            ),
        )
    return builder.as_markup()