from StaticData import StaticData
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram import F
import keyboards
import requests
import datetime


@StaticData.dp.callback_query(F.data == "cancel")
async def cancel(callback: types.CallbackQuery, state: FSMContext):
    if not StaticData.logged_in(callback.message.chat.id):
        await StaticData.bot.edit_message_text(f"Добро пожаловать в панель управления!", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_login_menu())
    else:
        user = StaticData.users[callback.message.chat.id]
        if "selected_bot" in user.keys():
            bot_name = user["selected_bot"]
            data = {
                "username": user["name"],
                "password": user["password"],
                "botname": bot_name
            }
            response = requests.post("http://192.168.31.55:6000/get_bot_status", data=data)
            if response.status_code == 200:
                bot_data = response.json()
                await StaticData.bot.edit_message_text(f"👋 Добро пожаловать в панель управления, {user["name"]}!\n" + \
                                                f"🤖 Текущий выбранный бот - {bot_name}\n" + \
                                                f"{"✅" if bot_data["status"] == "running" else "❌"} Статус бота: {bot_data["status"]} \n" + \
                                                f"💰 Стоимость бота: {bot_data["price"]}₽ \n" + \
                                                f"⏰ Следующая оплата бота: {parse_date(bot_data["next_payment_date"]) if bot_data["next_payment_date"] != None else "None"} \n" + \
                                                "Вот список доступных Вам команд: ", 
                                        chat_id=callback.message.chat.id, 
                                        message_id=callback.message.message_id,
                                        reply_markup=keyboards.get_main_menu(message=callback.message))
            else:
                await StaticData.bot.edit_message_text(f"Произошла ошибка: {response.text}", 
                                        chat_id=callback.message.chat.id, 
                                        message_id=callback.message.message_id,
                                        reply_markup=keyboards.get_cancel_keyboard())
                user.pop("selected_bot")
        else:
            await StaticData.bot.edit_message_text(f"Добро пожаловать в панель управления, {user["name"]}!\n" + \
                                                "Вот список доступных Вам команд: ", 
                                        chat_id=callback.message.chat.id, 
                                        message_id=callback.message.message_id,
                                        reply_markup=keyboards.get_main_menu(message=callback.message))
        
    await state.clear()
    await callback.answer()

def parse_date(date):
    date = datetime.datetime.fromtimestamp(date)
    return f"{(date.day if len(str(date.day)) == 2 else f"0{date.day}")}.{(date.month if len(str(date.month)) == 2 else f"0{date.month}")}.{date.year}"