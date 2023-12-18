# bot URL: https://t.me/nyle_bi_controller_bot
import os
from io import StringIO
from threading import Thread

import bottle
import colorama
import pandas as pd

import telebot
from bottle import request
from telebot import types
from telebot.apihelper import ApiTelegramException

import database
import payload_manager_new as payload_manager
import state
from helpers import get_all_asins_from_text, log
from state import chunk

bot = telebot.TeleBot('6907121969:AAFxNOUoBwata5M_YEXwGj_dGanLN6ct1gc', parse_mode='Markdown')
auth_users = {320753905, 1428909514}
PASSWORD = '12345'
processes = set()


def send_msg(user_id, message, *args, **kwargs):
    log(f'Message to {user_id}: "{message}"')
    return bot.send_message(user_id, message, *args, **kwargs)


def receive_message(msg: types.Message):
    log(f'Receive message from {msg.from_user.id}:', msg.text)


def auth(msg: types.Message):
    return msg.from_user.id in auth_users


def get_asins_data(msg: types.Message, **kwargs):
    receive_message(msg)
    if msg.text in ('/close', '/stop', '/quit'):
        return send_msg(msg.from_user.id, 'Cancel')
    asins_raw = msg.text.replace('/get_asins_data', '').strip()
    if asins_raw:
        asins = set(get_all_asins_from_text(asins_raw))
        if asins:
            if 'list_name' in kwargs:
                payload_manager.add_reviews_tasks(asins, msg.from_user.id)
                payload_manager.add_products_task(asins, kwargs['list_name'], msg.from_user.id)
                return send_msg(
                    msg.from_user.id,
                    f'Process started. We\'ll notify you when it is completed. List name: {kwargs["list_name"]}',
                )
            kwargs.update({'asins': asins})
            return bot.register_next_step_handler(send_msg(
                msg.from_user.id, 'Enter the list name:'),
                get_asins_data, **kwargs,
            )
        if 'asins' in kwargs:
            payload_manager.add_reviews_tasks(kwargs['asins'], msg.from_user.id)
            payload_manager.add_products_task(kwargs['asins'], asins_raw, msg.from_user.id)
            return send_msg(
                msg.from_user.id,
                f'Process started. We\'ll notify you when it is completed. List name: {asins_raw}',
            )
        kwargs.update({'list_name': asins_raw})
        return bot.register_next_step_handler(send_msg(
            msg.from_user.id,
            f'List name: {asins_raw}. Enter the ASINs list:'), get_asins_data, **kwargs,
        )
    return bot.register_next_step_handler(send_msg(msg.from_user.id, 'Enter the ASINs list:'), get_asins_data)


def export_asins(msg: types.Message, **kwargs):
    receive_message(msg)
    if msg.text in ('/close', '/stop', '/quit'):
        return send_msg(msg.from_user.id, 'Cancel')
    asins_raw = msg.text.replace('/export_asins', '').strip()
    if asins_raw:
        asins = set(get_all_asins_from_text(asins_raw))
        if asins:
            kwargs.update({'asins': asins})
            if 'list_name' in kwargs and 'collections' in kwargs:
                collections = (('amazon_data.customer_reviews', 'amazon_data.product_card')
                               if kwargs['collections'] == 'amadata' else kwargs['collections'])
                for collection in collections:
                    _export_asins(asins, msg.from_user.id, collection, kwargs['list_name'])
                return
            if 'list_name' in kwargs:
                return bot.register_next_step_handler(send_msg(
                    msg.from_user.id,
                    f'Filename: {kwargs["list_name"]}. Enter the collection ([database].[collection] or amadata):',
                    parse_mode='HTML',
                ), export_asins, **kwargs)
            return bot.register_next_step_handler(send_msg(
                msg.from_user.id, 'Enter the filename:'),
                export_asins, **kwargs,
            )
        if 'asins' in kwargs:
            if 'list_name' in kwargs:
                collections = (('amazon_data.customer_reviews', 'amazon_data.product_card')
                               if asins_raw == 'amadata' else asins_raw)
                for collection in collections:
                    _export_asins(kwargs['asins'], msg.from_user.id, collection, kwargs['list_name'])
                return
            kwargs.update({'list_name': asins_raw})
            return bot.register_next_step_handler(send_msg(
                msg.from_user.id, f'Filename: {asins_raw}. Enter the collection ([database].[collection] or amadata):',
                parse_mode='HTML',
            ), export_asins, **kwargs)
        if 'list_name' in kwargs:
            if asins_raw == 'amadata':
                asins_raw = 'amazon_data.customer_reviews,amazon_data.product_card'
            kwargs.update({'collections': asins_raw.split(',')})
            return bot.register_next_step_handler(send_msg(
                msg.from_user.id,
                f'Filename: {kwargs["list_name"]}; Collections: {asins_raw}. Enter the ASINs list:',
                parse_mode='HTML',
            ), export_asins, **kwargs)
        kwargs.update({'list_name': asins_raw})
        return bot.register_next_step_handler(send_msg(
            msg.from_user.id,
            f'Filename: {asins_raw}. Enter the ASINs list:',
            parse_mode='HTML',
        ), export_asins, **kwargs)
    return bot.register_next_step_handler(send_msg(msg.from_user.id, 'Enter the ASINs list:'), export_asins)


def _export_asins(asins_list, user_id, location='amazon_data.customer_reviews', list_name=None):
    asins = set(asins_list)
    db_col = location.split('.')
    if len(db_col) != 2:
        return send_msg(user_id, f'Invalid collection: {location}!\nWrite it like this: amazon_data.customer_reviews'
                                 '([database].[collection] or "amadata" (reviews+products))', parse_mode='HTML')
    db_name, collection = db_col
    if not asins:
        return send_msg(user_id, f'No product found: {asins_list}')
    data = database.db(db_name)[collection].find({'asin': {'$in': list(asins)}})
    cols_mapping = {
        'amazon_data.customer_reviews':
            'helpful,country,name,rating,review_id,date,scrap_datetime,title,description,asin,product_url,options'
            .split(','),
    }
    try:
        cols = cols_mapping.get(location, list(data[0].keys() - ['_id']))
    except IndexError:
        cols = []
    df = pd.DataFrame(columns=cols)
    for row in data:
        df.loc[len(df.index)] = row
    if not os.path.exists('tmp'):
        os.mkdir('tmp')
    path = os.path.join('tmp', f'{location}.{(list_name if list_name else str(hash(df.loc)))}.csv')
    df.to_csv(path, index=False)
    with open(path, 'rb') as doc:
        bot.send_document(user_id, doc)
    os.remove(path)


@bot.message_handler(content_types=['document'])
def import_asins_doc(msg: types.Message, **kwargs):
    return import_asins(msg, **kwargs)


def import_asins(msg: types.Message, **kwargs):
    receive_message(msg)
    if msg.text in ('/close', '/stop', '/quit'):
        return send_msg(msg.from_user.id, 'Cancel')
    if msg.document:
        try:
            file_info = bot.get_file(msg.document.file_id)
        except ApiTelegramException:
            return send_msg(msg.from_user.id, 'File size is over than 20MB!')
        doc = bot.download_file(file_info.file_path)
        if 'collection' in kwargs:
            return _import_asins(msg.from_user.id, doc, kwargs['collection'])
        return bot.register_next_step_handler(
            send_msg(msg.from_user.id, 'Enter the collection ([database].[collection]):', parse_mode='HTML'),
            import_asins, document=doc,
        )
    collection_raw = msg.text.replace('/import_asins', '').strip()
    if collection_raw:
        if 'document' in kwargs:
            return _import_asins(msg.from_user.id, kwargs['document'], collection_raw)
        return bot.register_next_step_handler(
            send_msg(msg.from_user.id, 'Send the CSV file:'),
            import_asins, collection=collection_raw,
        )
    return bot.register_next_step_handler(
        send_msg(msg.from_user.id, 'Enter the collection ([database].[collection]):', parse_mode='HTML'),
        import_asins,
    )


def _import_asins(user_id, document, location):
    try:
        df = pd.read_csv(StringIO(document.decode('utf-8')))
    except Exception as e:
        return send_msg(user_id, f'Error occurred: {str(e)}', parse_mode='HTML')
    db_col = location.split('.')
    if len(db_col) != 2:
        return send_msg(user_id, f'Collection is incorrect: {location}', parse_mode='HTML')
    db_name, collection = db_col
    try:
        try:
            database.db(db_name)[collection].insert_many(df.T.to_dict().values())
        except Exception:
            database.spec_db(db_name)[collection].insert_many(df.T.to_dict().values())
        return send_msg(user_id, f'Data inserted successfully to {location}!', parse_mode='HTML')
    except Exception as e:
        return send_msg(user_id, f'Error occurred: {str(e)}', parse_mode='HTML')


def delete_asins(msg: types.Message):
    receive_message(msg)
    asins_raw = msg.text.replace('/delete_asins', '').strip()
    if asins_raw:
        for args in (
            (get_all_asins_from_text(asins_raw), msg.from_user.id),
            (get_all_asins_from_text(asins_raw), msg.from_user.id, 'raw_product_card_htmls'),
            (get_all_asins_from_text(asins_raw), msg.from_user.id, 'product_card', 'amazon_data', 'products'),
            (get_all_asins_from_text(asins_raw), msg.from_user.id, 'aspects', 'ai_highlights'),
            (get_all_asins_from_text(asins_raw), msg.from_user.id, 'top_phrases', 'ai_highlights'),
            (get_all_asins_from_text(asins_raw), msg.from_user.id, 'problems', 'ai_highlights'),
        ):
            if not _delete_asins(*args):
                break
        return send_msg(msg.from_user.id, 'These ASINs deleted successfully')
    return bot.register_next_step_handler(send_msg(msg.from_user.id, 'Please enter the ASINs list:'), delete_asins)


def _delete_asins(asins_list, user_id, collection='customer_reviews', db_name='amazon_data', _type='reviews'):
    asins = set(asins_list)
    if not asins:
        send_msg(user_id, 'No valid ASIN found')
        return False
    try:
        try:
            database.db(db_name)[collection].delete_many({'asin': {'$in': list(asins)}})
        except:
            database.spec_db(db_name)[collection].delete_many({'asin': {'$in': list(asins)}})
        if _type is not None:
            with open(os.path.join('states', f'collect-{_type}.state')) as f:
                all_asins = set(chunk(f.read().strip()))
            for asin in asins:
                st = state.get_asin(asin, _type)
                if st == -1:
                    all_asins.remove(asin)
                elif st > 0 and os.path.exists(os.path.join('states', f'collect-{_type}-{asin}.currstate')):
                    os.remove(os.path.join('states', f'collect-{_type}-{asin}.currstate'))
            with open(os.path.join('states', f'collect-{_type}.state'), 'w') as f:
                f.write(''.join(all_asins))
        return True
    except Exception as e:
        send_msg(user_id, 'Error occurred: {}'.format(e), parse_mode='HTML')
        return False


def unknown(msg: types.Message):
    return send_msg(msg.from_user.id, 'Unknown command')


CMDs = {
    'get_asins_data': get_asins_data,
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


@bot.message_handler(commands=['cmd'], func=auth)
def cmds(msg: types.Message):
    return bot.send_message(msg.from_user.id, 'All commands:\n/' + '\n/'.join(CMDs.keys()), reply_markup=buttons(),
                            parse_mode='HTML')


def non_verification_user_msg(msg: types.Message):
    receive_message(msg)
    if msg.text.strip() == PASSWORD:
        auth_users.add(msg.from_user.id)
        send_msg(msg.from_user.id, 'Login success! You can use all bot functions!')
        return
    send_msg(msg.from_user.id, 'Verification failed. Please enter the master password')


### BOTTLE REQUESTS
def run_bottle():
    @bottle.route('/send_msg', method='POST')
    def send_message():
        msg = request.forms.get('msg')
        users_ids = request.forms.get('uid').split(',')
        if request.files:
            for file in request.files:
                for uid in users_ids:
                    try:
                        bot.send_document(uid, request.files[file].file, visible_file_name=request.files[file].filename)
                    except:
                        pass
        if msg:
            for uid in users_ids:
                bot.send_message(uid, msg)

    @bottle.route('/end_task', method='POST')
    def end_task():
        _id = request.forms.get('_id')
        payload_manager.end_task(_id)

    bottle.run(host='0.0.0.0', port=8080, debug=True)


if __name__ == '__main__':
    for cmd in CMDs:
        dcmd = CMDs[cmd]
        bot.register_message_handler(callback=dcmd, commands=[cmd], func=auth)
    bot.register_message_handler(callback=non_verification_user_msg, func=lambda msg: not auth(msg))
    bot.register_message_handler(callback=unknown, func=lambda _: True)
    bottle_thr = Thread(target=run_bottle, daemon=True)
    bottle_thr.start()
    bot.infinity_polling()
