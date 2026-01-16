import os
import asyncio
from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message
import httpx
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
YOUR_USER_ID = int(os.getenv("YOUR_TELEGRAM_USER_ID"))
API_URL = os.getenv("PREDICTIONS_API_URL", "http://localhost:8000/api/predictions")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start", "help"])
async def cmd_start(message: Message):
    if message.from_user.id != YOUR_USER_ID:
        return
    await message.answer("Привет! Используй /predictions для получения актуальных прогнозов.")

@dp.message_handler(commands=["predictions"])
async def send_predictions(message: Message):
    if message.from_user.id != YOUR_USER_ID:
        await message.answer("Доступ запрещён.")
        return

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(API_URL)
            if resp.status_code != 200:
                raise Exception(f"API error: {resp.status_code}")
            data = resp.json()
        
        if not 
            await message.answer("Нет активных прогнозов на ближайшие 48 часов.")
            return

        text = "🔥 Прогнозы (уверенность ≥70%):\n\n"
        for p in 
            dt = datetime.fromisoformat(p['match_datetime'].replace("Z", "+00:00"))
            text += (
                f"📅 {dt.strftime('%d.%m %H:%M')}\n"
                f"🏆 {p['league']}\n"
                f"{p['home_team']} – {p['away_team']}\n"
                f"🎯 {p['prediction_type']} ({int(p['confidence']*100)}%)\n"
            )
            if p.get('reasoning'):
                text += f"📝 {p['reasoning']}\n"
            text += "\n"

        # Ограничение Telegram: 4096 символов
        if len(text) > 4000:
            parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
            for part in parts:
                await message.answer(part)
        else:
            await message.answer(text)

    except Exception as e:
        await message.answer(f"❌ Ошибка при загрузке прогнозов:\n{str(e)}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)