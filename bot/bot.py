import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router, F
from aiogram.enums import ChatMemberStatus
from aiogram.types import Message, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.markdown import hlink
import json
import hmac, hashlib, os
import aiohttp
import uvicorn
import asyncio
from fastapi import FastAPI, Request

load_dotenv()
# Цена темплейта
price_per_template = 100

# Переменные
TOKEN = os.getenv("token_by_bot")
CHANNEL_USERNAME = "@mixbyvasilpapi"

# Инициализация
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

bot_app = FastAPI()

# 🔐 Проверка подписки
async def is_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]
    except Exception as e:
        return False


# /start
@router.message(F.text == "/start")
async def start(message: Message):

    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="🔥 Забрать чеклист")],
        [KeyboardButton(text="💽 Купить темплейт")],
        [KeyboardButton(text="🎚 Заказать сведос")]
    ])
    await message.answer(
        "🎙 Салют! \n"
        "Здесь можно забрать материалы, апнуть звук и двинуться на новый уровень.  \n"
        "Выбери, что тебе интересно:",
        reply_markup=kb
    )


# 🔥 Забрать чеклист
@router.message(F.text == "🔥 Забрать чеклист")
async def checklist(message: Message):
    text = (
        "📘 Чеклист “Запиши как надо” — мини-гайд для тех, кто хочет звучать и быть услышанным.\n"
        "Собрано из опыта 100+ проектов. Доступен только подписчикам канала.\n"
        f"Подпишись на канал 👉 {hlink('mixbyvasilpapi', 'https://t.me/mixbyvasilpapi')}\n"
        "Потом нажми “Получить” и забери файл.\n"
        "⏳ Telegram может обновить статус через пару секунд."
    )

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Получить", callback_data="get_pdf")]
    ])

    await message.answer(text, reply_markup=markup)

# 💽 Купить темплейт
@router.message(F.text == "💽 Купить темплейт")
async def buy_template(message: Message):
    text = (
        "🎛 Темплейт от HopOutSound\n"
        "Это не просто пресет. Это целая схема, как получить плотный, сочный вокал, не лезя в дебри.\n"
        f"Цена: {price_per_template}₽\n"
        "👇 Нажми “Оплатить”, чтобы забрать."
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💸 Оплатить", url="https://t.me/tribute/app?startapp=dtub")]
    ])
    await message.answer(text, reply_markup=markup)



@bot_app.post("/send_pdf")
async def send_pdf(request: Request):
    data = await request.json()
    telegram_id = data.get("telegram_id")
    amount = data.get("amount")
    if not telegram_id:
        return {"error": "telegram_id missing"}
    try:
        if amount is not None and amount >= price_per_template:
            file = FSInputFile("files_for_money/test.txt")
            await bot.send_document(
                chat_id=telegram_id,
                document=file,
                caption=f"🎉 Спасибо за донат на сумму {amount}₽!\nВот, лови темплейт!"
            )
            return {"status": "sent"}
        else:
            print("Зашел в else")
            text = (
                f"🎉 Спасибо за донат на сумму {amount}₽!\n"
                f"Для получения темплейта нужно {price_per_template}₽."
                if amount is not None else
                "Спасибо! Не получил сумму платежа. Если это ошибка — напиши мне."
            )
            await bot.send_message(chat_id=telegram_id, text=text)   # <-- ВАЖНО
            return {"status": "thanks_only"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


# 🎚 Заказать сведос
@router.message(F.text == "🎚 Заказать сведос")
async def order_mixing(message: Message):
    text = (
        "🎚 Заказать сведос\n"
        "Здесь ты получаешь звук, который не стыдно показать.\n"
        "⚠️ Сначала обсудим задачу, потом оплата.\n"
        "👇 Нажми “Связаться”, напишу тебе лично."
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📬 Связаться", url="https://t.me/hopoutsound")]
    ])
    await message.answer(text, reply_markup=markup)


# ✅ Получить PDF
@router.callback_query(F.data == "get_pdf")
async def send_pdf(callback: CallbackQuery):
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id

    if await is_subscribed(user_id):
        try:
            pdf_file = FSInputFile("files_for_free/Test.pdf")
            await bot.send_document(chat_id, pdf_file, caption="📘 Лови! Запиши как надо — твой.")
        except Exception:
            await bot.send_message(chat_id, "Произошла ошибка при отправке файла.")
    else:
        await callback.answer("Ты не подписан на канал!", show_alert=True)


# 🔁 Запуск бота
if __name__ == "__main__":

    async def main():
        # Запускаем бота и FastAPI вместе
        loop = asyncio.get_running_loop()
        loop.create_task(dp.start_polling(bot))

        config = uvicorn.Config(bot_app, host="0.0.0.0", port=8001, loop="asyncio")
        server = uvicorn.Server(config)
        await server.serve()

    asyncio.run(main())