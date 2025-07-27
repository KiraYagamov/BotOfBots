from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from StaticData import StaticData
import requests

def get_cancel_keyboard(text="Отмена"):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text=text,
        callback_data="cancel"
    ))
    return builder.as_markup()

def get_ok_keyboard(text="ОК"):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text=text,
        callback_data="ok"
    ))
    return builder.as_markup()

def get_login_menu():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="Войти",
        callback_data="login"
    ))
    return builder.as_markup()

def get_main_menu(message=None):
    user = None
    if message != None:
        if StaticData.logged_in(message.chat.id):
            user = StaticData.users[message.chat.id]
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="Выбрать бота",
        callback_data="select_bot"
    ))
    if user != None:
        if "selected_bot" in user.keys():
            builder.row(
                types.InlineKeyboardButton(
                    text="Обновить бота",
                    callback_data="update_bot"
                ),
                types.InlineKeyboardButton(
                    text="Добавить зависимости",
                    callback_data="add_dependencies"
                )
            )
            builder.row(types.InlineKeyboardButton(
                text="Запустить бота",
                callback_data="start_bot"
            ))
            builder.row(
                types.InlineKeyboardButton(
                    text="Остановить бота",
                    callback_data="stop_bot"
                ),
                types.InlineKeyboardButton(
                    text="Перезапустить",
                    callback_data="restart_bot"
                )
            )
            builder.row(types.InlineKeyboardButton(
                text="Скачать файлы бота",
                callback_data="download_bot_files"
            ))
            builder.row(types.InlineKeyboardButton(
                text="Скачать логи бота",
                callback_data="download_bot_logs"
            ))
    if user != None:
        if user["privilege"] in ["ADMIN", "MAIN_ADMIN"]:
            builder.row(types.InlineKeyboardButton(
                text="Открыть админ-панель",
                callback_data="open_admin_panel"
            ))
    builder.row(types.InlineKeyboardButton(
        text="Выйти из аккаунта",
        callback_data="logout"
    ))
    return builder.as_markup()

def get_admin_menu():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="Создать бота",
            callback_data="create_bot"
        ),
        types.InlineKeyboardButton(
            text="Удалить бота",
            callback_data="remove_bot"
        ),
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Вывести список ботов",
            callback_data="get_bots_list"
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Присвоить бота",
            callback_data="assign_bot"
        ),
        types.InlineKeyboardButton(
            text="Отнять бота",
            callback_data="take_away_bot"
        ),
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Установить цену",
            callback_data="set_price"
        ),
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Установить дату оплаты",
            callback_data="set_payment_date"
        ),
        types.InlineKeyboardButton(
            text="Продлить бота на месяц",
            callback_data="prolong_bot"
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Запустить рассылку",
            callback_data="run_newsletter"
        ),
    )
    builder.row(types.InlineKeyboardButton(
        text="Вернуться в меню",
        callback_data="cancel"
    ))
    return builder.as_markup()