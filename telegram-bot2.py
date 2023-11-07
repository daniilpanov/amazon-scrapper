# bot URL: https://t.me/nyle_bi_controller_bot

import telebot
from telebot import types
from multiprocessing import Process

import main_collect_all

bot = telebot.TeleBot('6907121969:AAFxNOUoBwata5M_YEXwGj_dGanLN6ct1gc', parse_mode='Markdown')

GET_ASINS = 'get_asins_data'
GET_ASINS_CMD = '/' + GET_ASINS
BTN_CMD_IDs = ((GET_ASINS_CMD, 'Get and process list of ASINs'),)

auth_users = [320753905]
users_active_commands = {}


# Log helper
def send_msg(user_id, message, *args, **kwargs):
    print(f'Sending message [{user_id}]: "{message}"')
    bot.send_message(user_id, message, *args, **kwargs)


def buttons():
    keyboard = types.InlineKeyboardMarkup()
    for cmd_id, descr in BTN_CMD_IDs:
        key = types.InlineKeyboardButton(text=descr, callback_data=cmd_id)
        keyboard.add(key)

    return keyboard


@bot.message_handler(commands=[GET_ASINS])
def get_asins_data(msg: types.Message):
    users_active_commands[msg.from_user.id] = GET_ASINS
    send_msg(msg.from_user.id, 'Please enter the ASINs list:')


@bot.message_handler(content_types=['text'])
def get_text_messages(msg: types.Message):
    if users_active_commands[msg.from_user.id] == GET_ASINS:
        send_msg(msg.from_user.id, 'Process started. We\'ll notify you when it is completed')
        make_process(msg.text.strip(), msg.from_user.id)
        return

    if msg.text.startswith(GET_ASINS_CMD):
        return make_process(msg.from_user.id, msg.text[len(GET_ASINS_CMD):])

    send_msg(msg.from_user.id, 'Unknown command')


def make_process(asins_list, user_id):
    # Create new process
    process = Process(target=main_collect_all.start())
    pass
