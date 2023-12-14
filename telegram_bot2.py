# bot URL: https://t.me/nyle_bi_controller_bot
import os

import bottle
import colorama
import pandas as pd
from subprocess import Popen
from threading import Thread

import telebot
from bottle import request
from telebot import types

import database
import payload_manager
import state
from helpers import get_all_asins_from_text
from state import chunk

bot = telebot.TeleBot('6907121969:AAFxNOUoBwata5M_YEXwGj_dGanLN6ct1gc', parse_mode='Markdown')
auth_users = {320753905, 1428909514}
processes = set()

DEBUG = True


def log(*args, **kwargs):
    if DEBUG:
        print(colorama.Back.GREEN, *args, colorama.Back.RESET, **kwargs)


def send_msg(user_id, message, *args, **kwargs):
    log(f'Message to {user_id}: "{message}"')
    return bot.send_message(user_id, message, *args, **kwargs)


def receive_message(msg: types.Message):
    log(f'Receive message from {msg.from_user.id}:', msg.text)


def auth(msg: types.Message):
    return msg.from_user.id in auth_users


def get_all_asins_data(msg: types.Message, *args, **kwargs):
    pass


def export_asins(msg: types.Message, *args, **kwargs):
    pass


def import_asins(msg: types.Message, *args, **kwargs):
    pass


def delete_asins(msg: types.Message, *args, **kwargs):
    pass


def buttons():
    keyboard = types.ReplyKeyboardMarkup()
    for cmd in CMDs:
        key = types.InlineKeyboardButton(text=CMDs[cmd][1], callback_data=cmd)
        keyboard.add(key)

    return keyboard


@bot.callback_query_handler(func=lambda *args, **kwargs: True)
def process_buttons():
    pass


CMDs = {
    'get_all_asins_data': (get_all_asins_from_text, 'Get All ASINs Data'),
    'export_asins': (export_asins, 'Export ASINs'),
    'import_asins': (import_asins, 'Import ASINs'),
    'delete_asins': (delete_asins, 'Delete ASINs'),
}


if __name__ == '__main__':
    for cmd in CMDs:
        dcmd = CMDs[cmd]
        bot.register_message_handler(callback=dcmd, commands=[cmd], func=auth)

    bot.infinity_polling()
