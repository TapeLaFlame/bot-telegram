import asyncio
import logging
import os
import sqlite3
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # Пример: -1001234567890

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# SQLite
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        expires_at TEXT
    )
""")
conn.commit()

# Кнопки
def get_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить 5€", callback_data="pay")],
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data="paid")]
    ])

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("SELECT expires_at FROM subscriptions WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if row and datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") > datetime.utcnow():
        await message.answer("✅ У вас активная подписка.")
    else:
        await message.answer("Добро пожаловать!\nПодписка: 5€ / 1 месяц", reply_markup=get_keyboard())

@dp.callback_query(F.data == "pay")
async def pay_handler(callback: types.CallbackQuery):
    await callback.message.answer("💳 Переведите 5€ на карту:\n<b>5354 5612 5103 8586</b>\n\nПосле оплаты нажмите «Я оплатил».", parse_mode="HTML")

@dp.callback_query(F.data == "paid")
async def paid_handler(callback: types.CallbackQuery):
    user = callback.from_user
    await bot.send_message(
        ADMIN_ID,
        f"🧾 <b>{user.full_name}</b> сообщил об оплате.\nID: <code>{user.id}</code>\nUsername: @{user.username}",
    )
    await callback.message.answer("Спасибо! Мы проверим оплату и откроем вам доступ.")

@dp.message(F.text.startswith("/confirm"))
async def confirm_user(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, user_id = message.text.strip().split()
        user_id = int(user_id)
        username = (await bot.get_chat(user_id)).username or "no_username"
        expires_at = datetime.utcnow() + timedelta(days=30)
        cursor.execute("REPLACE INTO subscriptions (user_id, username, expires_at) VALUES (?, ?, ?)",
                       (user_id, username, expires_at.strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        invite_link = await bot.create_chat_invite_link(chat_id=CHANNEL_ID, member_limit=1)
        await bot.send_message(user_id, f"✅ Оплата подтверждена. Вот ваша ссылка: {invite_link.invite_link}")
        await message.answer("Пользователю выдан доступ.")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")

async def check_expired_users():
    while True:
        await asyncio.sleep(3600)  # проверка каждый час
        cursor.execute("SELECT user_id, expires_at FROM subscriptions")
        for user_id, expires in cursor.fetchall():
            try:
                if datetime.strptime(expires, "%Y-%m-%d %H:%M:%S") < datetime.utcnow():
                    await bot.ban_chat_member(CHANNEL_ID, user_id)
                    await bot.unban_chat_member(CHANNEL_ID, user_id)
                    cursor.execute("DELETE FROM subscriptions WHERE user_id = ?", (user_id,))
                    conn.commit()
                    await bot.send_message(ADMIN_ID, f"❌ Пользователь {user_id} удалён — подписка истекла.")
            except Exception as e:
                logging.error(f"Ошибка удаления {user_id}: {e}")

async def main():
    logging.basicConfig(level=logging.INFO)
    asyncio.create_task(check_expired_users())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
