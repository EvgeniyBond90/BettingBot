import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
import httpx
from datetime import datetime
from aiogram.exceptions import TelegramRetryAfter

# Маппинг коротких названий лиг → полные названия
LEAGUE_FULL_NAMES = {
    "АПЛ": "Англия - Премьер-лига",
    "Ла Лига": "Испания - Ла Лига",
    "Сегунда": "Испания - Сегунда",
    "Серия А": "Италия - Серия А",
    "Серия B": "Италия - Серия B",
    "Серия С - группа А": "Италия - Серия С, группа А",
    "Серия С - группа B": "Италия - Серия С, группа B",
    "Серия С - группа C": "Италия - Серия С, группа C",
    "Бундеслига": "Германия - Бундеслига",
    "Бундеслига 2": "Германия - Бундеслига 2",
    "Лига 1": "Франция - Лига 1",
    "Лига 2": "Франция - Лига 2",
    "Эредивизи": "Нидерланды - Эредивизи",
    "Примейра Лига": "Португалия - Примейра Лига",
    "Жупиле Лига": "Бельгия - Жупиле Лига",
    "Немзети лига": "Венгрия - Немзети лига",
    "Суперлига": "Турция - Суперлига",
    "РПЛ": "Россия - РПЛ",
    "Премьер-лига Украины": "Украина - Премьер-лига",
    "Премьер-лига Шотландии": "Шотландия - Премьер-лига",
    "Чехия - Экстракласа": "Чехия - Экстракласа",
    "Бундеслига (Австрия)": "Австрия - Бундеслига",
    "Суперлига (Швейцария)": "Швейцария - Суперлига",
    "Суперлига (Дания)": "Дания - Суперлига",
    "Элитесерия": "Норвегия - Элитесерия",
    "Оллсвенскан": "Швеция - Оллсвенскан",
    "Вейккауслига": "Финляндия - Вейккауслига",
    "Суперлига (Греция)": "Греция - Суперлига",
    "Прва ХНЛ": "Хорватия - Прва ХНЛ",
    "Приморье (Словения)": "Словения - Приморье",
    "Суперлига Сербии": "Сербия - Суперлига",
    "Лига I": "Румыния - Лига I",
    "Първа лига": "Болгария - Първа лига",
    "Немзети байноксаг": "Венгрия - Немзети байноксаг",
    "Словацкая экстралига": "Словакия - Экстралига",
    "Прва лига БиГ": "Босния и Герцеговина - Прва лига",
    "Суперлига (Албания)": "Албания - Суперлига",
    "Прва лига (Македония)": "Северная Македония - Прва лига",
    "Высшая лига (Латвия)": "Латвия - Высшая лига",
    "А-лига (Литва)": "Литва - А-лига",
    "Меистрилига": "Эстония - Меистрилига",
    "Национальная лига (Молдавия)": "Молдавия - Национальная лига",
    "Премьер-лига Армении": "Армения - Премьер-лига",
    "Премьер-лига Азербайджана": "Азербайджан - Премьер-лига",
    "Премьер-лига Казахстана": "Казахстан - Премьер-лига",
    "Джей-лига": "Япония - Джей-лига",
    "K-лига": "Южная Корея - K-лига",
    "A-League": "Австралия - A-League",
    "Персидская лига": "Иран - Персидская лига",
    "1-я лига (Индонезия)": "Индонезия - 1-я лига",
    "Лига чемпионов УЕФА": "Европа - Лига чемпионов УЕФА",
    "Лига Европы УЕФА": "Европа - Лига Европы УЕФА",
    "Лига конференций УЕФА": "Европа - Лига конференций УЕФА"
}

# Получаем токен и ID из переменных окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
YOUR_USER_ID = int(os.getenv("YOUR_TELEGRAM_USER_ID"))

# URL к API админки (замените на ваш домен)
API_URL = os.getenv("PREDICTIONS_API_URL", "https://194.32.248.172/api/predictions")

# Логин и пароль для HTTP Basic Auth
API_USERNAME = os.getenv("API_USERNAME", "admin")
API_PASSWORD = os.getenv("API_PASSWORD", "password")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: Message):
    if message.from_user.id != YOUR_USER_ID:
        await message.reply("Доступ запрещён.")
        return
    await message.reply("Привет! Используй /predictions для получения прогнозов.")

@dp.message(Command("predictions"))
async def send_predictions(message: Message):
    if message.from_user.id != YOUR_USER_ID:
        await message.reply("Доступ запрещён.")
        return

    try:
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            response = await client.get(API_URL, auth=(API_USERNAME, API_PASSWORD))

        if response.status_code != 200:
            await message.reply(f"Ошибка: API вернул статус {response.status_code}")
            return

        data = response.json()

        if not data:
            await message.reply("Нет активных прогнозов.")
            return

        text = "⚽ Прогнозы:\n\n"
        for item in data:
            dt_str = item['match_datetime']
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))

            # Получаем полное название лиги, если оно есть
            league_full = LEAGUE_FULL_NAMES.get(item['league'], item['league'])

            text += (
                f"📅 {dt.strftime('%d.%m %H:%M')}\n"
                f"🏆 {league_full}\n"
                f"⚽ {item['home_team']} – {item['away_team']}\n"
                f"🔮 {item['prediction_type']}\n\n"
            )

        await message.reply(text.strip())

    except TelegramRetryAfter as e:
        # Обработка лимита отправки
        await asyncio.sleep(e.retry_after)
        try:
            await message.reply("Повторная отправка...")
            await message.reply(text.strip())
        except:
            await message.reply("Не удалось отправить — лимит превышен.")
    except Exception as e:
        await message.reply(f"Ошибка при получении прогнозов: {str(e)}")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
