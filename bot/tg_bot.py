from typing import Sequence

from telebot import types, TeleBot
from loguru import logger

from core.settings import bot_settings
from core.models import CashAction
from db import create_tables, get_engine
from db.queries import (
    user_exists,
    create_new_user,
    add_new_location,
    add_new_money,
    update_money,
    get_user_locations,
    get_location_id,
    get_user_locations_with_money
)

engine = get_engine()
create_tables(engine)
bot = TeleBot(bot_settings.bot_token)


def send_menu(chat_id: int, buttons: Sequence[str], text: str = "") -> None:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for button in buttons:
        markup.row(types.KeyboardButton(button))

    bot.send_message(chat_id, text=text, reply_markup=markup)


def menu(chat_id):
    send_menu(chat_id, bot_settings.menu_buttons, text="Menu:")


@bot.message_handler(commands=["start"])
def start(msg):
    user_id = msg.from_user.id
    logger.info(f"start message received from {user_id=}")
    bot.send_message(msg.chat.id, "Hi! We're gonna help you to track your cash savings💵")
    menu(msg.chat.id)


def add_location_callback(msg):
    user_id = msg.from_user.id
    user_nickname = msg.from_user.username
    location_name = msg.text
    with engine.connect() as conn:
        if not user_exists(user_id=user_id, conn=conn):
            logger.info(f"Creating new user {user_id}: {user_nickname}")
            create_new_user(user_id=user_id, nickname=user_nickname, conn=conn)
            logger.success(f"Created new user {user_id}: {user_nickname}")
        logger.info(f"Creating new location {location_name} for user {user_id}")
        location_id = add_new_location(user_id=user_id, name=location_name, conn=conn)
        logger.success(f"Created new location {location_name} for user {user_id}")

    bot.send_message(user_id, text=f"{location_name} location added")
    bot.send_message(user_id, text=f"How much money do you store in location {location_name}?")
    bot.register_next_step_handler_by_chat_id(
        chat_id=msg.chat.id, callback=add_new_location_cash_callback, location_id=location_id
    )


def add_new_location_cash_callback(msg, location_id: int) -> None:
    user_id = msg.from_user.id
    amount = int(msg.text)
    logger.info(f"Adding new cash for user {user_id}")
    with engine.connect() as conn:
        add_new_money(user_id=user_id, location_id=location_id, amount=amount, conn=conn)
    logger.success(f"Added new cash for user {user_id}")
    bot.send_message(user_id, text="Cool! Wrote that to the database")
    menu(user_id)


def select_cash_amount_callback(msg, action: CashAction) -> None:
    user_id = msg.from_user.id
    location_name = msg.text

    bot.send_message(user_id, text="Enter amount:")
    bot.register_next_step_handler_by_chat_id(
        chat_id=msg.chat.id, callback=update_cash_callback, location_name=location_name, action=action
    )


def update_cash_callback(msg, location_name: str, action: CashAction) -> None:
    user_id = msg.from_user.id
    amount = int(msg.text)
    if action == CashAction.withdraw:
        amount = -amount
    logger.info(f"Adding cash for user {user_id}")
    with engine.connect() as conn:
        location_id = get_location_id(user_id=user_id, location_name=location_name, conn=conn)
        update_money(user_id=user_id, location_id=location_id, amount=amount, conn=conn)
    logger.success(f"Updated cash for user {user_id}")
    bot.send_message(user_id, text="Cool! Wrote that to the database")
    menu(user_id)


@bot.message_handler(func=lambda msg: msg.text == "Get my locations")
def get_locations(msg):
    user_id = msg.from_user.id
    logger.info(f"get locations message received from {user_id=}")
    with engine.connect() as conn:
        data = get_user_locations_with_money(user_id=user_id, conn=conn)
    bot.send_message(user_id, text=str(data), parse_mode="Markdown")
    menu(user_id)


@bot.message_handler(func=lambda msg: msg.text == "Add location")
def add_location(msg):
    user_id = msg.from_user.id
    logger.info(f"add location message received from {user_id=}")
    bot.send_message(chat_id=msg.chat.id, text="Choose new location name")
    bot.register_next_step_handler_by_chat_id(chat_id=msg.chat.id, callback=add_location_callback)


@bot.message_handler(func=lambda msg: msg.text == "Add cash")
def add_cash(msg):
    user_id = msg.from_user.id
    logger.info(f"add cash message received from {user_id=}")

    locations = get_user_locations(user_id=user_id, engine=engine)
    send_menu(chat_id=user_id, buttons=locations, text="Select location:")
    bot.register_next_step_handler_by_chat_id(
        chat_id=msg.chat.id, callback=select_cash_amount_callback, action=CashAction.add
    )


@bot.message_handler(func=lambda msg: msg.text == "Withdraw cash")
def withdraw_cash(msg):
    user_id = msg.from_user.id
    logger.info(f"withdraw location message received from {user_id=}")
    locations = get_user_locations(user_id=user_id, engine=engine)
    send_menu(chat_id=user_id, buttons=locations, text="Select location:")
    bot.register_next_step_handler_by_chat_id(
        chat_id=msg.chat.id, callback=select_cash_amount_callback, action=CashAction.withdraw
    )
