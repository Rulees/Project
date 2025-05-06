from dotenv import load_dotenv
import os
import asyncio
from aiogram import Bot, Dispatcher
from bot_scripts.handlers import router
from bot_scripts.db import init_db
from bot_scripts.handlers import reminder_task, send_review_link_task
import logging



TOKEN = os.getenv("TOKEN")


bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(router)


async def start_background_tasks():
    asyncio.create_task(reminder_task(bot))
    asyncio.create_task(send_review_link_task(bot))


async def main():
    await init_db()
    print("🚀 Bot is running...")
    await dp.start_polling(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await start_background_tasks()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot Stopped')
    except Exception as e:
        logging.info('Error {not important}')