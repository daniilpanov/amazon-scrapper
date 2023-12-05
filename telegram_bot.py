# bot URL: https://t.me/nyle_bi_controller_bot
import os

import pandas as pd
from multiprocessing import Pipe
from threading import Thread

import telebot
from telebot import types

import database
import payload_manager
import state
from helpers import get_all_asins_from_text

bot = telebot.TeleBot('6907121969:AAFxNOUoBwata5M_YEXwGj_dGanLN6ct1gc', parse_mode='Markdown')
server_reader, client_writer = Pipe(False)
queue, collect_thread = payload_manager.init(client_writer)

GET_ASINS = 'get_asins_data'
CSV_EXPORT_ASINS = 'export_asins'
DELETE_ASINS = 'delete_asins'
GET_ASINS_CMD = '/' + GET_ASINS
CSV_EXPORT_ASINS_CMD = '/' + CSV_EXPORT_ASINS
DELETE_ASINS_CMD = '/' + DELETE_ASINS
BTN_CMDs = (
    (GET_ASINS, 'Get and process list of ASINs'),
    (CSV_EXPORT_ASINS, 'Export all data of ASINs in the CSV format'),
    (DELETE_ASINS, 'Remove all ASINs from given list'),
)
PASSWORD = '12345'

auth_users = {320753905, 1428909514}
processes = []


# Log helpers
def send_msg(user_id, message, *args, **kwargs):
    print(f'Message to {user_id}: "{message}"')
    return bot.send_message(user_id, message, *args, **kwargs)


def receive_msg(msg: types.Message):
    print(f'Receive message from {msg.from_user.id}:', msg.text)


def check_login(msg: types.Message):
    return msg.from_user.id in auth_users


def buttons():
    keyboard = types.InlineKeyboardMarkup()
    for cmd_id, descr in BTN_CMDs:
        key = types.InlineKeyboardButton(text=descr, callback_data=cmd_id)
        keyboard.add(key)

    return keyboard


# BOT INTERFACE
@bot.message_handler(commands=[GET_ASINS], func=check_login)
def get_asins_msg_cmd(msg: types.Message):
    receive_msg(msg)
    asins_raw = msg.text.replace(GET_ASINS_CMD, '').strip()
    if asins_raw:
        return get_asins(get_all_asins_from_text(asins_raw), msg.from_user.id)
    bot.register_next_step_handler(send_msg(msg.from_user.id, 'Please enter the ASINs list:'), get_asins_msg)


@bot.message_handler(commands=[CSV_EXPORT_ASINS], func=check_login)
def export_asins_cmd(msg: types.Message):
    receive_msg(msg)
    list_name = msg.text.replace(CSV_EXPORT_ASINS_CMD, '').strip()
    if list_name:
        return bot.register_next_step_handler(
            send_msg(msg.from_user.id, 'Please enter the ASINs list:'),
            export_asins_msg,
            list_name=list_name,
        )
    bot.register_next_step_handler(
        send_msg(msg.from_user.id, 'Please enter the name of the ASINs list:'),
        export_asins_name_list_msg,
    )


@bot.message_handler(commands=[DELETE_ASINS], func=check_login)
def delete_asins_cmd(msg: types.Message):
    receive_msg(msg)
    asins_raw = msg.text.replace(DELETE_ASINS_CMD, '').strip()
    if asins_raw:
        delete_asins(get_all_asins_from_text(asins_raw), msg.from_user.id)
        return delete_asins(get_all_asins_from_text(asins_raw), msg.from_user.id, 'product_card')
    bot.register_next_step_handler(send_msg(msg.from_user.id, 'Please enter the ASINs list:'), delete_asins_msg)


def get_asins_msg(msg: types.Message):
    receive_msg(msg)
    if not check_login(msg):
        return
    get_asins(get_all_asins_from_text(msg.text.strip()), msg.from_user.id)


def export_asins_name_list_msg(msg: types.Message):
    receive_msg(msg)
    if not check_login(msg):
        return
    bot.register_next_step_handler(
        send_msg(msg.from_user.id, 'Please enter the ASINs list:'),
        export_asins_msg,
        list_name=msg.text.strip(),
    )


def export_asins_msg(msg: types.Message, list_name=None):
    receive_msg(msg)
    if not check_login(msg):
        return
    export_asins(get_all_asins_from_text(msg.text.strip()), msg.from_user.id, list_name=list_name)
    export_asins(get_all_asins_from_text(msg.text.strip()), msg.from_user.id, 'product_card', list_name)


def delete_asins_msg(msg: types.Message):
    receive_msg(msg)
    if not check_login(msg):
        return
    delete_asins(get_all_asins_from_text(msg.text.strip()), msg.from_user.id)
    delete_asins(get_all_asins_from_text(msg.text.strip()), msg.from_user.id, 'product_card')


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


def get_asins(asins_list, user_id):
    # Create new process
    asins = set(asins_list)
    if not asins:
        return bot.send_message(user_id, 'No valid ASIN detected')
    send_msg(user_id, 'Process started. We\'ll notify you when it is completed')
    queue.put((asins, callback, user_id))


def export_asins(asins_list, user_id, collection='customer_reviews', list_name=None):
    asins = set(asins_list)
    if not asins:
        return bot.send_message(user_id, 'No product found')
    data = database.db()[collection].find({'asin': {'$in': list(asins)}})
    df = pd.DataFrame(columns=(data[0].keys() - ['_id']))
    for row in data:
        df.loc[len(df.index)] = row
    if not os.path.exists('tmp'):
        os.mkdir('tmp')
    path = os.path.join('tmp', list_name + ' (' + collection + ').csv' if list_name else str(hash(df.loc)) + '.csv')
    df.to_csv(path, index=False)
    with open(path, 'rb') as doc:
        bot.send_document(user_id, doc)
    os.remove(path)


def delete_asins(asins_list, user_id, collection='customer_reviews'):
    asins = set(asins_list)
    if not asins:
        return bot.send_message(user_id, 'No valid ASIN found')
    try:
        database.db()[collection].delete_many({'asin': {'$in': list(asins)}})
        if not os.path.exists('states/collect-reviews.state'):
            return
        with open('states/collect-reviews.state') as f:
            asins = f.read()
        for asin in asins:
            st = state.get_asin(asin)
            if st == -1:
                asins = asins.replace(asin, '')
            elif st:
                os.remove('states/collect-reviews-{}.currstate'.format(asin))
        with open('states/collect-reviews.state', 'w') as f:
            f.write(asins)
        bot.send_message(user_id, 'These ASINs deleted successfully')
    except Exception as e:
        bot.send_message(user_id, 'Error occurred: {}'.format(e))


def products_alerts():
    while True:
        res = server_reader.recv()
        print(res)
        if not res:
            break
        chat_id, res = res
        bot.send_message(chat_id, f'Product cards of those ASIN\'s collected: {",".join(res)}')


if __name__ == '__main__':
    print('PROGRAM STARTED')
    alerts_thr = Thread(target=products_alerts)
    alerts_thr.start()
    buttons()
    bot.infinity_polling()
    print('PROGRAM IS CLOSING ALL TASKS')
    queue.put(None)
    payload_manager.close_all()
    client_writer.send(False)
    alerts_thr.join()
    collect_thread.join()
    print('PROGRAM ENDED')
