import os
import json
import sqlite3
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import uvicorn

API_TOKEN = '8227759215:AAHGhF_RgsB5ZY4Kyn3KRWD9511eAqwKB7o'
WEB_APP_URL = 'https://ryntsk.github.io/queue-app/'
# URL твоего будущего сервиса на Render (получишь после деплоя)
BASE_URL = "https://твой-проект.onrender.com"

# Инициализация
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
app = FastAPI()

# Разрешаем таблице обращаться к серверу
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def init_db():
    with sqlite3.connect('queue.db') as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS queue (slot INTEGER PRIMARY KEY, name TEXT)')


# API для таблицы: получить текущую очередь
@app.get("/get_queue")
async def get_queue():
    with sqlite3.connect('queue.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT slot, name FROM queue')
        return {str(row[0]): row[1] for row in cursor.fetchall()}


# Бот: команда Старт
@dp.message(F.text == "/start")
async def start(message: types.Message):
    init_db()
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открыть живую очередь", web_app=WebAppInfo(url="ТВОЯ_ССЫЛКА_GITHUB"))]
    ])
    await message.answer("Нажми кнопку, чтобы видеть очередь в реальном времени:", reply_markup=markup)


# Прием данных из Web App
@dp.message(F.content_type == types.ContentType.WEB_APP_DATA)
async def web_app(message: types.Message):
    data = json.loads(message.web_app_data.data)
    slot = data['slot']
    name = message.from_user.first_name

    with sqlite3.connect('queue.db') as conn:
        try:
            conn.execute('INSERT INTO queue (slot, name) VALUES (?, ?)', (slot, name))
            await message.answer(f"✅ {name}, ты на месте №{slot}")
        except:
            await message.answer("❌ Это место уже заняли!")


# Запуск всего вместе
async def run_bot():
    await dp.start_polling(bot)


@app.on_event("startup")
async def startup():
    init_db()
    asyncio.create_task(run_bot())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))