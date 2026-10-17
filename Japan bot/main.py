from os import getenv
import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from aiogram_sentinel import Sentinel, SentinelConfig

from routers.routery import router

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

if not TOKEN:
    print("❌ ОШИБКА: Токен не найден!")
    print(f"Текущая директория: {os.getcwd()}")
    print("Проверьте файл .env в папке:", os.path.dirname(os.path.abspath(__file__)))
    exit(1)
else:
    print(f"✅ Токен загружен ({len(TOKEN)} символов)")


dp = Dispatcher()


async def main():
    # Sentinel нужно подключать здесь, где есть dp
    sentinel_config = SentinelConfig(debounce_default_window=2)
    sentinel_router, infra = await Sentinel.setup(dp, sentinel_config)

    # Порядок важен: сначала sentinel_router, потом ваш router
    dp.include_router(router)

    bot = Bot(token=TOKEN)
    print("Active ! ! !")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())