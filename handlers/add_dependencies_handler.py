from StaticData import StaticData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import types
from aiogram import F
import keyboards
import requests

class AddDependenciesState(StatesGroup):
    uploading_file = State()


@StaticData.dp.callback_query(F.data == "add_dependencies")
async def add_dependencies(callback: types.CallbackQuery, state: FSMContext):
    if StaticData.logged_in(callback.message.chat.id):
        user = StaticData.get_user(callback.message.chat.id)
        await state.update_data(user=user)
        await state.update_data(callback=callback)
        await state.set_state(AddDependenciesState.uploading_file)
        await StaticData.bot.edit_message_text(f"Отправьте файл requirements.txt", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_cancel_keyboard())
    else:
        await StaticData.bot.edit_message_text(f"Для начала войдите в аккаунт!", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_login_menu())
        await state.clear()
        await callback.answer()

@StaticData.dp.message(AddDependenciesState.uploading_file)
async def uploading_file(message: types.Message, state: FSMContext):
    file = message.document
    await StaticData.bot.delete_message(message.chat.id, message.message_id)
    user_data = await state.get_data()
    user = user_data["user"]
    callback = user_data["callback"]
    if file == None:
        await StaticData.bot.edit_message_text(f"Файл не был отправлен!", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_cancel_keyboard())
    else:
        file_info = await StaticData.bot.get_file(message.document.file_id)
        downloaded_file = await StaticData.bot.download_file(file_info.file_path)
        downloaded_file.name = file.file_name
        data = {
            "username": user["name"],
            "password": user["password"],
            "botname": user["selected_bot"]
        }
        files = {"file": downloaded_file}
        response = requests.post("http://192.168.31.55:6000/add_dependencies", data=data, files=files, stream=True)
        if response.status_code == 200:
            await StaticData.bot.edit_message_text(f"Файл отправлен!", 
                                        chat_id=callback.message.chat.id, 
                                        message_id=callback.message.message_id,
                                        reply_markup=keyboards.get_cancel_keyboard())
        else:
            await StaticData.bot.edit_message_text(f"Что-то пошло не так...", 
                                        chat_id=callback.message.chat.id, 
                                        message_id=callback.message.message_id,
                                        reply_markup=keyboards.get_cancel_keyboard())
    await state.clear()
