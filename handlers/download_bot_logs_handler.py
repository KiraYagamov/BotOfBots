from StaticData import StaticData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import FSInputFile
from aiogram import types
from aiogram import F
import keyboards
import requests
import os
import subprocess

@StaticData.dp.callback_query(F.data == "download_bot_logs")
async def download_bot_logs(callback: types.CallbackQuery, state: FSMContext):
    if StaticData.logged_in(callback.message.chat.id):
        user = StaticData.users[callback.message.chat.id]
        data = {
            "username": user["name"],
            "password": user["password"],
            "botname": user["selected_bot"]
        }
        response = requests.post("http://192.168.31.55:6000/get_logs", data=data, stream=True)
        if response.status_code == 200:
            filename = "logs.txt"

            if response.text == "":
                await StaticData.bot.edit_message_text(f"Логов нет!", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_cancel_keyboard())
                await state.clear()
                await callback.answer()
                return

            with open(filename, "w") as f:
                f.write(response.text)
            
            subprocess.run(["sync"])
                
            file = FSInputFile(filename)

            await StaticData.bot.edit_message_text(f"Ваши логи бота:", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_cancel_keyboard())
            await StaticData.bot.send_document(
                callback.message.chat.id,
                file,
                reply_markup=keyboards.get_ok_keyboard()
            )
            try:
                os.remove(filename)
            except:
                print("Не удалось удалить файл!")
        else:
            await StaticData.bot.edit_message_text(f"Произошла ошибка при получении логов бота!", 
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

