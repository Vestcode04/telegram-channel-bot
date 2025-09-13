import asyncpg
import os
from dotenv import load_dotenv
from aiogram import Router
from aiogram.types import Message

load_dotenv()

db_router = Router()

# функция для подключения к БД
async def get_connection():
    conn = await asyncpg.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    return conn

# инициализация таблицы
async def init_db():
    conn = await get_connection()
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            chat_id BIGINT NOT NULL,
            message_id BIGINT NOT NULL,
            text TEXT,
            date TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """)
    await conn.close()


# сохранение сообщения
async def save_message(chat_id: int, message_id: int, text: str):
    conn = await get_connection()
    await conn.execute("""
        INSERT INTO messages (chat_id, message_id, text)
        VALUES ($1, $2, $3)
    """, chat_id, message_id, text)
    await conn.close()

# хэндлер для постов в канале
@db_router.channel_post()
async def handle_channel_post(message: Message):
    if message.text:
        await save_message(message.chat.id, message.message_id, message.text)

# получение сообщений за последний месяц
async def get_messages_from_db() -> list[str]:
    conn = await get_connection()
    rows = await conn.fetch("""
        SELECT text FROM messages
        WHERE date >= NOW() - INTERVAL '30 days'
    """)
    await conn.close()
    return [row['text'] for row in rows if row['text']]

