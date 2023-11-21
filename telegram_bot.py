# bot URL: https://t.me/nyle_bi_controller_bot
import re
from multiprocessing import Pipe
from threading import Thread

import telebot
from telebot import types

import payload_manager

bot = telebot.TeleBot('6907121969:AAFxNOUoBwata5M_YEXwGj_dGanLN6ct1gc', parse_mode='Markdown')
server_reader, client_writer = Pipe(False)
queue, collect_thread = payload_manager.init(client_writer)

GET_ASINS = 'get_asins_data'
GET_ASINS_CMD = '/' + GET_ASINS
BTN_CMD_IDs = ((GET_ASINS_CMD, 'Get and process list of ASINs'),)
PASSWORD = '12345'

auth_users = {320753905}
processes = []


# Log helpers
def send_msg(user_id, message, *args, **kwargs):
    print(f'Message to {user_id}: "{message}"')
    return bot.send_message(user_id, message, *args, **kwargs)


# Parse raw asins list from TG message or file or other
def get_all_asins_from_text(text: str):
    pattern_find = re.compile('[A-Z0-9]{10}')
    asins = set()
    for line in text.strip().splitlines():
        found = pattern_find.findall(line)
        for item in found:
            asins.add(item)
    return list(asins)


def receive_msg(msg: types.Message):
    print(f'Receive message from {msg.from_user.id}:', msg.text)


def check_login(msg: types.Message):
    return msg.from_user.id in auth_users


def buttons():
    keyboard = types.InlineKeyboardMarkup()
    for cmd_id, descr in BTN_CMD_IDs:
        key = types.InlineKeyboardButton(text=descr, callback_data=cmd_id)
        keyboard.add(key)

    return keyboard


# BOT INTERFACE
@bot.message_handler(commands=[GET_ASINS], func=check_login)
def get_asins_data(msg: types.Message):
    receive_msg(msg)
    asins_raw = msg.text.replace(GET_ASINS_CMD, '').strip()
    if asins_raw:
        return make_process(asins_raw, msg.from_user.id)
    bot.register_next_step_handler(send_msg(msg.from_user.id, 'Please enter the ASINs list:'), get_asins)


def get_asins(msg: types.Message):
    receive_msg(msg)
    if not check_login(msg):
        return
    make_process(msg.text.strip(), msg.from_user.id)


@bot.message_handler(content_types=['text'], func=check_login)
def get_text_messages(msg: types.Message):
    receive_msg(msg)
    send_msg(msg.from_user.id, 'Unknown command')


@bot.message_handler(func=lambda _: True)
def non_verification_user_msg(msg: types.Message):
    receive_msg(msg)
    if msg.text.strip() == PASSWORD:
        auth_users.add(msg.from_user.id)
        send_msg(msg.from_user.id, 'Login success! You can use all bot functions!')
        return
    send_msg(msg.from_user.id, 'Verification failed. Please enter the master password')


def callback(uid, asin):
    send_msg(uid, f'Reviews of ASIN collected: {asin}')


def make_process(asins_list_raw, user_id):
    # Create new process
    send_msg(user_id, 'Process started. We\'ll notify you when it is completed')
    asins = set(get_all_asins_from_text(asins_list_raw))
    queue.put((asins, callback, (user_id,)))


def products_alerts():
    while True:
        res = server_reader.recv()
        if not res:
            break
        chat_id, res = res
        bot.send_message(chat_id, f'Product cards of those ASIN\'s collected: {",".join(res)}')


if __name__ == '__main__':
    print('PROGRAM STARTED')
    alerts_thr = Thread(target=products_alerts)
    alerts_thr.start()
    bot.infinity_polling()
    print('PROGRAM IS CLOSING ALL TASKS')
    payload_manager.close_all()
    client_writer.send(False)
    alerts_thr.join()
    print('PROGRAM ENDED')
