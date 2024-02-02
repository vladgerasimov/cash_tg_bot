from loguru import logger

from bot import bot

if __name__ == '__main__':
    logger.info("Starting bot ...")
    bot.infinity_polling()
