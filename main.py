import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ChatMemberUpdated
from aiogram.enums.chat_member_status import ChatMemberStatus
import sqlite3

API_TOKEN = "YOUR_BOT_TOKEN"
CHANNEL_ID = -1002641870797
ADMIN_ID = 634825131

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
conn.commit()

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    if message.text == "/start":
        cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()

        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            await message.answer("Сначала подпишитесь на канал.")
            return

        await bot.send_message(user_id, "Добро пожаловать! Доступ разрешён.")

@dp.my_chat_member()
async def handle_join(event: ChatMemberUpdated):
    if event.new_chat_member.status == ChatMemberStatus.MEMBER:
        await bot.send_message(event.from_user.id, "Спасибо за подписку!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
