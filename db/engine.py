import sqlalchemy
from loguru import logger

from core.settings import bot_settings


def get_engine() -> sqlalchemy.Engine | None:
    try:
        return sqlalchemy.create_engine(bot_settings.db_url)
    except Exception as e:
        logger.warning(e)
        return None
