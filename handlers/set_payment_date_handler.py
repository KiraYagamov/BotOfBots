from StaticData import StaticData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from aiogram import F
import keyboards
import requests
import datetime

class SetPaymentDateState(StatesGroup):
    selecting_bot = State()
    setting_date = State()

@StaticData.dp.callback_query(F.data.split(";")[0] == "set_payment_date")
async def set_payment_date(callback: types.CallbackQuery, state: FSMContext):
    if StaticData.logged_in(callback.message.chat.id):
        user = StaticData.users[callback.message.chat.id]
        user_state = await state.get_state()
        if user_state != SetPaymentDateState.selecting_bot:
            bots = get_bots_list(user)
            if bots != -1:
                await state.set_state(SetPaymentDateState.selecting_bot)
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
        await StaticData.bot.edit_message_text(f"Для начала войдите в аккаунт!", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_login_menu())
        await state.clear()
        await callback.answer()

@StaticData.dp.callback_query(F.data.split(";")[0] == "pick_bot_payment")
async def pick_bot_payment(callback: types.CallbackQuery, state: FSMContext):
    if callback.message.chat.id in StaticData.users.keys():
        user = StaticData.users[callback.message.chat.id]
        bot_name = callback.data.split(";")[1]
        await state.update_data(selected_bot=bot_name)
        await state.set_state(SetPaymentDateState.setting_date)
        await StaticData.bot.edit_message_text(f"Введите дату оплаты в формате dd-MM-YYYY", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_cancel_keyboard())
        await callback.answer()
    else:
        await StaticData.bot.edit_message_text(f"Для начала войдите в аккаунт!", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_login_menu())
        await state.clear()
        await callback.answer()

@StaticData.dp.message(SetPaymentDateState.setting_date)
async def setting_date(message: types.Message, state: FSMContext):
    if StaticData.logged_in(message.chat.id):
        user = StaticData.users[message.chat.id]
        date_text = message.text
        user_data = await state.get_data()
        callback = user_data["callback"]
        await StaticData.bot.delete_message(message.chat.id, message.message_id)
        try:
            date = parse_date(date_text)
            data = {
                "username": user["name"],
                "password": user["password"],
                "botname": user_data["selected_bot"],
                "timestamp": date
            }
            response = requests.post("http://192.168.31.55:6000/set_bot_payment_date", data=data)
            if response.status_code == 200:
                await StaticData.bot.edit_message_text(f"Дата успешно установлена!", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_cancel_keyboard())
            else:
                await StaticData.bot.edit_message_text(f"Произошла ошибка при установке даты! ", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_cancel_keyboard())
        except:
            await StaticData.bot.edit_message_text(f"Дата введена неверно!", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_cancel_keyboard())
            await state.clear()
    else:
        await StaticData.bot.edit_message_text(f"Для начала войдите в аккаунт!", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_login_menu())
        await state.clear()

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
            callback_data=f"pick_bot_payment;{bots_list[i]}"
        ))
    if 1 < page < max_page:
        builder.row(
            types.InlineKeyboardButton(
                text="<",
                callback_data=f"set_payment_date;{max(page-1, 1)}"
            ),
            types.InlineKeyboardButton(
                text=">",
                callback_data=f"set_payment_date;{min(page+1, max_page)}"
            ),
        )
    elif max_page == 1:
        pass
    elif page == 1:
        builder.row(
            types.InlineKeyboardButton(
                text=">",
                callback_data=f"set_payment_date;{min(page+1, max_page)}"
            ),
        )
    elif page == max_page:
        builder.row(
            types.InlineKeyboardButton(
                text="<",
                callback_data=f"set_payment_date;{max(page-1, 1)}"
            ),
        )
    return builder.as_markup()

def parse_date(date):
    date_format = "%d-%m-%Y"
    datetime_obj = datetime.datetime.strptime(date, date_format)
    return datetime_obj.timestamp()
