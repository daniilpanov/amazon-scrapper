# bot URL: https://t.me/nyle_bi_controller_bot
import os
import sys

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


def new_process(script, *args, stdin=None, stdout=None, stderr=None, **kwargs):
    return Popen(
        [sys.executable, script + '.py', *args, *list(key + '=' + kwargs[key] for key in kwargs)],
        stdin=stdin or sys.stdin, stdout=stdout or sys.stdout, stderr=stderr or sys.stderr,
    )


def send_msg(user_id, message, *args, **kwargs):
    log(f'Message to {user_id}: "{message}"')
    return bot.send_message(user_id, message, *args, **kwargs)


def receive_message(msg: types.Message):
    log(f'Receive message from {msg.from_user.id}:', msg.text)


def auth(msg: types.Message):
    print('ok!')
    return msg.from_user.id in auth_users


def get_asins_data(msg: types.Message, **kwargs):
    if not auth(msg):
        return msg
    receive_message(msg)
    if msg.text in ('/close', '/stop', '/quit'):
        return send_msg(msg.from_user.id, 'Cancel')
    asins_raw = msg.text.replace('/get_asins_data ', '').strip()
    if asins_raw:
        asins = set(get_all_asins_from_text(asins_raw))
        if asins:
            if 'list_name' in kwargs:
                new_process('main_collect_all', asins=''.join(asins), list_name=kwargs['list_name'])
                return send_msg(msg.from_user.id, 'Process started. We\'ll notify you when it is completed')
            kwargs.update({'asins': asins})
            return bot.register_next_step_handler(send_msg(msg.from_user.id, 'Enter the list name:'), get_asins_data, **kwargs)
        if 'asin' in kwargs:
            log('')
            new_process('main_collect_all', asins=''.join(kwargs['asins']), list_name=asins_raw)
            return send_msg(msg.from_user.id, 'Process started. We\'ll notify you when it is completed')
        kwargs.update({'list_name': asins_raw})
        return bot.register_next_step_handler(send_msg(msg.from_user.id, 'Enter the ASINs list:'), get_asins_data, **kwargs)
    return bot.register_next_step_handler(send_msg(msg.from_user.id, 'Please enter the ASINs list:'), get_asins_data)



def export_asins(msg: types.Message, *args, **kwargs):
    pass


def import_asins(msg: types.Message, *args, **kwargs):
    pass


def delete_asins(msg: types.Message, *args, **kwargs):
    pass


def unknown(msg: types.Message):
    return send_msg(msg.from_user.id, 'Unknown command')


CMDs = {
    'get_all_asins_data': get_asins_data,
    'export_asins': export_asins,
    'import_asins': import_asins,
    'delete_asins': delete_asins,
}


def buttons():
    keyboard = types.ReplyKeyboardMarkup()
    for cmd in CMDs:
        key = types.InlineKeyboardButton(text='/' + cmd)
        keyboard.add(key)

    return keyboard


@bot.message_handler(commands=['cmd'])
def cmds(msg: types.Message):
    return bot.send_message(msg.from_user.id, 'All commands:\n/' + '\n/'.join(CMDs.keys()), reply_markup=buttons(), parse_mode='HTML')


if __name__ == '__main__':
    for cmd in CMDs:
        dcmd = CMDs[cmd]
        bot.register_message_handler(callback=dcmd, commands=[cmd], func=auth)
    bot.register_message_handler(callback=unknown, func=lambda _: True)
    bot.infinity_polling()
