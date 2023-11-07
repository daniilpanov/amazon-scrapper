# bot URL: https://t.me/nyle_bi_controller_bot

import telebot
from telebot import types
from multiprocessing import Process

import main_collect_all

bot = telebot.TeleBot('6907121969:AAFxNOUoBwata5M_YEXwGj_dGanLN6ct1gc', parse_mode='Markdown')

GET_ASINS = 'get_asins_data'
GET_ASINS_CMD = '/' + GET_ASINS
BTN_CMD_IDs = ((GET_ASINS_CMD, 'Get and process list of ASINs'),)
PASSWORD = '12345'

auth_users = {320753905}
users_active_commands = {}


# Log helpers
def send_msg(user_id, message, *args, **kwargs):
    print(f'Message to {user_id}: "{message}"')
    bot.send_message(user_id, message, *args, **kwargs)


def receive_msg(msg: types.Message):
    print(f'Receive message from {msg.from_user.id}', msg.text)


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
    content = msg.text.replace(GET_ASINS_CMD, '').strip()
    if content:
        return make_process(content, msg.from_user.id)
    users_active_commands[msg.from_user.id] = GET_ASINS
    send_msg(msg.from_user.id, 'Please enter the ASINs list:')


@bot.message_handler(content_types=['text'], func=check_login)
def get_text_messages(msg: types.Message):
    receive_msg(msg)
    if users_active_commands.get(msg.from_user.id) == GET_ASINS:
        make_process(msg.text.strip(), msg.from_user.id)
        users_active_commands[msg.from_user.id] = None
        return

    send_msg(msg.from_user.id, 'Unknown command')


@bot.message_handler(func=lambda _: True)
def non_verification_user_msg(msg: types.Message):
    receive_msg(msg)
    if msg.text.strip() == PASSWORD:
        auth_users.add(msg.from_user.id)
        send_msg(msg.from_user.id, 'Login success! You can use all bot functions!')
        return
    send_msg(msg.from_user.id, 'Verification failed. Please enter the master password')


def make_process(asins_list_raw, user_id):
    # Create new process
    send_msg(user_id, 'Process started. We\'ll notify you when it is completed')
    process = Process(target=main_collect_all.start, args=(
        main_collect_all.get_all_asins_from_text(asins_list_raw),
    ), kwargs={'callback': lambda: send_msg(user_id, f'List of this ASINs is ready!\n{asins_list_raw}')})
    process.start()


if __name__ == '__main__':
    bot.infinity_polling()
