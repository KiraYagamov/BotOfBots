from aiogram import Bot, Dispatcher
from config import config
import requests

class StaticData:
    bot = Bot(
        token=config.bot_token.get_secret_value(),
    )
    dp = Dispatcher()
    users = {}
    def logged_in(chatID):
        return chatID in StaticData.users.keys()

    def get_user(chatID):
        return StaticData.users[chatID]
    
    def load_logged_in_users():
        response = requests.get("http://192.168.31.55:6000/get_logged_in_users")
        if response.status_code == 200:
            result = response.json()
            for user in result:
                data = {
                    "name": user["username"],
                    "password": user["password"],
                    "privilege": user["privilege"]
                }
                if user["selected_bot"] != None:
                    data["selected_bot"] = user["selected_bot"]
                StaticData.users[user["chatID"]] = data