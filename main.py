import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import aiosqlite

API_TOKEN = "YOUR_API_TOKEN"
ADMIN_ID = 634825131
REQUIRED_CHANNEL_ID = -1002641870797

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(REQUIRED_CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def create_db():
    async with aiosqlite.connect("users.db") as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)")
        await db.commit()

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    if not await check_subscription(user_id):
        await message.answer("Подпишитесь на канал, чтобы использовать бота.")
        return

    async with aiosqlite.connect("users.db") as db:
        await db.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
        await db.commit()

    if user_id == ADMIN_ID:
        await message.answer("Добро пожаловать, админ!")
    else:
        await message.answer("Добро пожаловать!")

if __name__ == "__main__":
    asyncio.run(create_db())
    executor.start_polling(dp, skip_updates=True)
