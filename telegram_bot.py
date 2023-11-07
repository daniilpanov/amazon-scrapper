# bot URL: https://t.me/nyle_bi_controller_bot

import telebot
from telebot import types

auth_users = [320753905]

bot = telebot.TeleBot('6907121969:AAFxNOUoBwata5M_YEXwGj_dGanLN6ct1gc', parse_mode='Markdown')

GET_ASINS = '/get_asins_data'
BTN_CMD_IDs = ((GET_ASINS, 'Get and process list of ASINs'),)

def buttons():
    keyboard = types.InlineKeyboardMarkup()
    for cmd_id, descr in BTN_CMD_IDs:
        key = types.InlineKeyboardButton(text=descr, callback_data=cmd_id)
        keyboard.add(key)
    
    return keyboard


def process_asins(user_id, str_asin_list):
    asins = str_asin_list.strip('\n ').split('\n')
    
    msg = f'Started ASINs {asins} processing'
    print(msg)
    bot.send_message(user_id, msg)

    # Processing code
    
    bot.send_message(user_id, f'Finished ASINs {asins} processing')

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    print(f'Received message: {message.text}')
    
    key = 'password'
    if message.text == key:
       auth_users.append(message.from_user.id)
       bot.send_message(message.from_user.id, f'{message.from_user.id} authenticated. {len(auth_users)}')
       return
    
    if not message.from_user.id in auth_users:
        msg = f'Unauthorized user id {message.from_user.id} message'
        print(msg)
        bot.send_message(message.from_user.id, msg)
        return
    
    res = 'unknown command'

    key = GET_ASINS
    if message.text.startswith(key):
        kl = len(key)
        return process_asins(message.from_user.id, message.text[kl:])
        
    send_msg_with_buttons(message.from_user.id, res)

    
def send_msg_with_buttons(uid, message):
    print(f'Sending message {message}')
    bot.send_message(uid, message, parse_mode='HTML', reply_markup=buttons()) 
    
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    
    res = 'unknown command'
    if call.data.startswith(GET_ASINS): #call.data это callback_data, которую мы указали при объявлении кнопки
        process_asins(call.message.chat.id, call.message.text)

bot.infinity_polling()
