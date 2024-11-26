from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from dotenv import load_dotenv
import os


load_dotenv()
ADMIN_id = os.getenv('ADMIN_id')
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# СТАРТ
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    try:
        first_name = message.chat.first_name
    except:
        first_name = 'Друг'
    web_app = types.WebAppInfo(url="https://bf5e-77-40-15-79.ngrok-free.app")
    menu_button = types.MenuButtonWebApp(f"Куда пойдем, {first_name} ? 🚶‍♂️", web_app=web_app)
    await bot.set_chat_menu_button(menu_button=menu_button)

def run_updater():
    executor.start_polling(dp)
