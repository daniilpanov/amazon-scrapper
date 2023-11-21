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
    make_process('''B0000BYCFU
B0002808ZM
B004PVR6V6
B00BLTCZ70
B00GJY6XI4
B00HCNHH2W
B00K7GIMCU
B00LU4CZP8
B015QFMNZI
B019GU4J56
B019ZZB3O2
B01IT9NLHW
B01M0JY15V
B06XR6NRYX
B079FNC379
B07G5KWZ3H
B07KF93DFH
B07S39J8JX
B07TXBWHYR
B07YDN7P1C
B07Z5LWMNZ
B081VSYKL5
B083F89ZC1
B0864S2FPR
B0866TKPMS
B08G8FK29N
B08LBBPJD9
B08SQTYTHJ
B08YKB6VMN
B094QB6PH6
B094QVRLKC
B094QWWLX2
B094QX6Y29
B099NX6SR8
B09F63F1HD
B09GKX9J39
B09H78YSNP
B09K7PG7P2
B09M473QHH
B09QKCV8LL
B09S5HSR2X
B09WLNXMJ5
B09ZL8BWDF
B0B1HZXWN2
B0B2D8J6G2
B0B6HQFKTZ
B0B9W324QZ
B0BGV79FHT
B0BHMR37T1
B0BNDRBSZ5
B0BRK8DKH8
B0BV6F7SXP
B0BWL4ZDC8
B0BX34T5PX
B0BX3N5D5P
B0BXFTSKC2
B0BYRL4PMR
B0BZHQCSJ6
B0BZHR5Z2L
B0BZVMN4M3
B0C4F514QW
B0C6X47WHN
B0C86W2MPR
B0CB68LHN9
B0CBMRCWYK
B0CHR9N12R
B07L6LYVFG
B07PF2PVQM
B07SW3LBNS
B07WPX9NF7
B07WS2YQ9J
B07WT7JHPZ
B07XYFDT2P
B07XYFXT65
B07XZH4VYN
B07YLG76QC
B07YLGV7V2
B07YTPH3PK
B081G9BVW6
B08NWBH2VC
B08S34T8JZ
B08VW4BNLR
B08YNGR4T7
B08ZNVPPMW
B08ZY2H8TR
B0914MG255
B0914X377J
B0919F6LTR
B091BGGWWY
B091BH3KLG
B093TTRTVH
B094HKRMW3
B09CNF43MF
B09JWRBXFY
B09JWV5926
B09KQXNZDC
B09NCKTSGZ
B09ZDPMR47
B09ZLFJ3L5
B0BB69P4K5
B0BB6P1DHY
B0BD743ZHX
B0BNKHY5DH
B0BWJFT7V4
''', 1428909514)
    alerts_thr = Thread(target=products_alerts)
    alerts_thr.start()
    bot.infinity_polling()
    print('PROGRAM IS CLOSING ALL TASKS')
    payload_manager.close_all()
    client_writer.send(False)
    alerts_thr.join()
    print('PROGRAM ENDED')
