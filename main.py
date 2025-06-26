import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import ChatAdminRequired
import sqlite3
import os

API_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456"))

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)")
conn.commit()

@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status not in ("member", "creator", "administrator"):
            raise Exception()
        cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
        conn.commit()
        await message.answer("✅ Доступ разрешён. Спасибо за подписку!")
    except:
        invite = await bot.export_chat_invite_link(CHANNEL_ID)
        await message.answer(f"🔒 Чтобы получить доступ, подпишитесь на канал: {invite}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
