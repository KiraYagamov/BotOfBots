from StaticData import StaticData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from aiogram import F
import keyboards
import requests

class RunNewsletterState(StatesGroup):
    entering_message = State()

@StaticData.dp.callback_query(F.data == "run_newsletter")
async def run_newsletter(callback: types.CallbackQuery, state: FSMContext):
    if StaticData.logged_in(callback.message.chat.id):
        user = StaticData.users[callback.message.chat.id]
        if user["privilege"] in ["ADMIN", "MAIN_ADMIN"]:
            await state.set_state(RunNewsletterState.entering_message)
            await state.update_data(callback=callback)
            await StaticData.bot.edit_message_text(f"Введите текст сообщения", 
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

@StaticData.dp.message(RunNewsletterState.entering_message)
async def entering_message(message: types.Message, state: FSMContext):
    chatids_of_users = StaticData.users.keys()
    newsletter = message.text
    await StaticData.bot.delete_message(message.chat.id, message.message_id)
    user_data = await state.get_data()
    callback = user_data["callback"]
    for chatid in chatids_of_users:
        await StaticData.bot.send_message(
            chatid,
            newsletter,
            reply_markup=keyboards.get_ok_keyboard("Хорошо")
        )
    await StaticData.bot.edit_message_text(f"Рассылка успешно отправлена!", 
                                    chat_id=callback.message.chat.id, 
                                    message_id=callback.message.message_id,
                                    reply_markup=keyboards.get_cancel_keyboard())
    await state.clear()
    await callback.answer()
