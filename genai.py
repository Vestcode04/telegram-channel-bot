import google.generativeai as genai
import os
from dotenv import load_dotenv
from db import get_messages_from_db 
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

load_dotenv()
ai_router = Router()

# Настройка Gemini
genai.configure(api_key=os.getenv('GEN_API'))
model = genai.GenerativeModel("gemini-2.0-flash")

async def analyze_messages(days: int = 30) -> str:
    # достаём сообщения из БД
    messages = await get_messages_from_db()

    if not messages:
        return "За этот период сообщений не найдено."

    # Склеиваем все сообщения в один текст
    text_data = "\n".join(messages)

    prompt = f"""
    Вот список сообщений из моего Telegram-канала за последние {days} дней:
    {text_data}

    Сделай краткий анализ:
    1. Какие темы чаще всего встречаются?
    2. Какие достижения можно выделить?
    3. Дай рекомендации для следующего месяца.
    """

    # асинхронный запрос к Gemini
    response = await model.generate_content_async(prompt)
    return response.text

@ai_router.message(Command("analyze"))
async def analyze_command(message: Message):
    await message.answer("🔍 Анализирую сообщения... Это может занять некоторое время.")
    analysis = await analyze_messages(30)
    await message.answer(f"📊 Анализ завершён:\n\n{analysis}")
