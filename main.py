import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = "ВАШ_ТОКЕН"
ADMIN_ID = 634825131  # ← сюда вставлен ваш Telegram ID
CHANNEL_ID = -1001234567890  # ← замените на ID вашего закрытого канала

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message()
async def start(message: Message):
    if message.text == "/start":
        kb = InlineKeyboardBuilder()
        kb.button(text="Подписка 5€", callback_data="subscribe")
        await message.answer("👋 Добро пожаловать!
Выберите тип подписки:", reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data == "subscribe")
async def process_subscription(callback: types.CallbackQuery):
    await callback.message.answer("💳 Переведите 5€ на карту: 5354 5612 5103 8586
После оплаты нажмите 'Готово'.")
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
