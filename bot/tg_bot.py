from typing import Sequence

from telebot import types, TeleBot
from loguru import logger

from core.settings import bot_settings
from db import get_engine

engine = get_engine()
bot = TeleBot(bot_settings.bot_token)


def send_menu(chat_id: int, buttons: Sequence[str]) -> None:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for button in buttons:
        markup.row(types.KeyboardButton(button))

    bot.send_message(chat_id, text="Menu:", reply_markup=markup)


def menu(chat_id):
    send_menu(chat_id, bot_settings.menu_buttons)


@bot.message_handler(commands=["start"])
def start(msg):
    user_id = msg.from_user.id
    logger.info(f"start message received from {user_id=}")
    bot.send_message(msg.chat.id, "Hi! We're gonna help you to track your cash savings💵")
    menu(msg.chat.id)


def get_locations_callback(msg):
    ...


def add_location_callback(msg):
    ...


def add_cash_callback(msg):
    ...


def withdraw_cash_callback(msg):
    ...


@bot.message_handler(func=lambda msg: msg.text == "Get my locations")
def get_locations(msg):
    user_id = msg.from_user.id
    logger.info(f"get locations message received from {user_id=}")
    get_locations_callback(msg)
    ...


@bot.message_handler(func=lambda msg: msg.text == "Add location")
def add_location(msg):
    user_id = msg.from_user.id
    logger.info(f"add location message received from {user_id=}")
    bot.send_message(chat_id=msg.chat.id, text="Choose new location name")
    bot.register_next_step_handler_by_chat_id(chat_id=msg.chat.id, callback=add_location_callback)
    ...


@bot.message_handler(func=lambda msg: msg.text == "Add cash")
def add_cash(msg):
    user_id = msg.from_user.id
    logger.info(f"add cash message received from {user_id=}")
    bot.send_message(chat_id=msg.chat.id, text="Choose location to add cash to")
    bot.register_next_step_handler_by_chat_id(chat_id=msg.chat.id, callback=add_cash_callback)
    ...


@bot.message_handler(func=lambda msg: msg.text == "Withdraw cash")
def withdraw_cash(msg):
    user_id = msg.from_user.id
    logger.info(f"withdraw location message received from {user_id=}")
    bot.send_message(chat_id=msg.chat.id, text="Choose location to withdraw cash from")
    bot.register_next_step_handler_by_chat_id(chat_id=msg.chat.id, callback=withdraw_cash_callback)
    ...
