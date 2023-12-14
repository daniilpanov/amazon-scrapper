# bot URL: https://t.me/nyle_bi_controller_bot
import os

import bottle
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


def receive_message(msg: types.Message):
    pass


def auth(msg: types.Message):
    return msg.from_user.id in auth_users


def get_all_asins_data(msg: types.Message):
    pass


def export_asins(msg: types.Message):
    pass


def import_asins(msg: types.Message):
    pass


def delete_asins(msg: types.Message):
    pass


def buttons():
    pass


def process_buttons():
    pass


CMDs = {
    'get_all_asins_data': get_all_asins_from_text,
    'export_asins': export_asins,
    'import_asins': import_asins,
    'delete_asins': delete_asins,
}

for cmd in CMDs:
    dcmd = CMDs[cmd]
    if type(dcmd) in (list, tuple, set, frozenset):
        func, auth_needle = dcmd
        if auth_needle:
            bot.register_message_handler(callback=func, commands=[cmd], func=auth)
        else:
            bot.register_message_handler(callback=func, commands=[cmd])
    else:
        bot.register_message_handler(callback=dcmd, commands=[cmd], func=auth)



