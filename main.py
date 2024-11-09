# main.py
import logging
import asyncio
import signal

import user_handlers
from config import load_config, Config
from aiogram import Bot, Dispatcher

from keyboard_menu import set_main_menu

# Загрузка переменных окружения
logger = logging.getLogger(__name__)

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logger.info('Starting bot')

    config: Config = load_config()
    bot = Bot(token=config.tg_bot.token) # получение токена из переменных окружения
    dp = Dispatcher() # Инициализация диспетчера
    await set_main_menu(bot) # Настройка кнопки меню

    dp.include_router(user_handlers.router) # Регистрация роутера
    await bot.delete_webhook(drop_pending_updates=True)

    # Запуск бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

    # Функция для корректного завершения polling
    async def shutdown():
        await dp.stop_polling()
        await bot.session.close()

    # Регистрация обработчиков сигналов для корректного завершения
    for sig in (signal.SIGINT, signal.SIGTERM):
        asyncio.get_running_loop().add_signal_handler(sig, lambda: asyncio.create_task(shutdown()))

    # Запуск polling для получения обновлений
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    print("Бот запущен!")
    asyncio.run(main())