# bot URL: https://t.me/nyle_bi_controller_bot
import functools
import json
import os
from io import StringIO
from threading import Thread

import bottle
import pandas
import pandas as pd

import telebot
from bottle import request
from pandas import DataFrame
from telebot import types
from telebot.apihelper import ApiTelegramException

import database
import payload_manager_new as payload_manager
import state
from helpers import get_all_asins_from_text, log
from state import chunk

bot = telebot.TeleBot('6907121969:AAFxNOUoBwata5M_YEXwGj_dGanLN6ct1gc')
auth_users = set()
PASSWORD = '12345'
CMDs = {}


def cmdreg(func, name=None):
    global CMDs

    def wrapper(msg: types.Message, *args, **kwargs):
        kwargs.setdefault('domain', 'amazon.com')
        receive_message(msg)
        if msg.text in ('/close', '/stop', '/quit', '/cancel', '/exit'):
            return send_msg(msg.from_user.id, 'Cancel')
        return func(msg, *args, **kwargs)

    CMDs[name or func.__name__] = wrapper
    bot.register_message_handler(callback=wrapper, commands=[name or func.__name__], func=auth)
    return wrapper


def send_msg(user_id, message, *args, **kwargs):
    log(f'Message to {user_id}: "{message}"')
    return bot.send_message(user_id, message, *args, **kwargs)


def receive_message(msg: types.Message):
    log(f'Receive message from {msg.from_user.id}:', msg.text)


def auth(msg: types.Message):
    return msg.from_user.id in auth_users


@cmdreg
def get_asins_data(msg: types.Message, **kwargs):
    asins_raw = msg.text.replace('/get_asins_data', '').strip()
    if asins_raw:
        asins = set(get_all_asins_from_text(asins_raw))
        if asins:
            if 'list_name' in kwargs:
                payload_manager.add_reviews_tasks(asins, msg.from_user.id, domain=kwargs['domain'])
                payload_manager.add_products_task(asins, kwargs['list_name'], msg.from_user.id, domain=kwargs['domain'])
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
            payload_manager.add_reviews_tasks(kwargs['asins'], msg.from_user.id, domain=kwargs['domain'])
            payload_manager.add_products_task(kwargs['asins'], asins_raw, msg.from_user.id, domain=kwargs['domain'])
            return send_msg(
                msg.from_user.id,
                f'Process started. We\'ll notify you when it is completed. List name: {asins_raw}',
            )
        kwargs.update({'list_name': asins_raw})
        return bot.register_next_step_handler(send_msg(
            msg.from_user.id,
            f'List name: {asins_raw}. Enter the ASINs list:'), get_asins_data, **kwargs,
        )
    return bot.register_next_step_handler(
        send_msg(msg.from_user.id, 'Enter the ASINs list:'),
        get_asins_data, **kwargs,
    )


cmdreg(functools.partial(get_asins_data, domain='amazon.com.mx'), 'get_asins_data_mx')


@cmdreg
def export_asins(msg: types.Message, **kwargs):
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
                               if asins_raw == 'amadata' else asins_raw.split(','))
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
        return send_msg(user_id, 'Empty file!')
    df = pd.DataFrame(columns=cols)

    for row in data:
        df.loc[len(df.index)] = row
    if not os.path.exists('tmp__'):
        os.mkdir('tmp__')
    path = os.path.join('tmp__', f'{location}.{(list_name if list_name else str(hash(df.loc)))}.csv')
    df.to_csv(path, index=False)
    with open(path, 'rb') as doc:
        bot.send_document(user_id, doc)
    os.remove(path)


@bot.message_handler(content_types=['document'])
def import_asins_doc(msg: types.Message, **kwargs):
    return import_asins(msg, **kwargs)


@cmdreg
def import_asins(msg: types.Message, **kwargs):
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


def ai_highlights_problems_mapping(data: DataFrame):
    head = set(data.columns.str.strip())
    needle_head = {'ASIN', 'Aspects', 'Description Problem', 'Problem'}
    if head != needle_head:
        raise Exception('Invalid header!')
    asins = data['ASIN'].tolist()
    database.spec_db('ai_highlights')['problems'].delete_many({'ASIN': {'$in': asins}})
    return data


def ai_highlights_aspects_new_mapping(data: DataFrame):
    data.columns = data.columns.str.strip()
    head = set(data.columns)
    if 'asin' not in head or 'review_id' not in head:
        raise Exception('Invalid header!')
    cols_for_drop = list(
        col for col in
        'helpful;country;name;rating;date;scrap_datetime;title;description;product_url;options;_id;content;product_url'
        .split(';') if col in head
    )
    data = data.drop(cols_for_drop, axis=1)
    new_data = pandas.melt(data, ['review_id', 'asin'], var_name='Aspect', value_name='Value')
    new_data = new_data.dropna(subset=new_data.columns)
    new_data['Aspect'] = new_data['Aspect'].str.strip()
    return new_data


def _import_asins(user_id, document, location):
    locations_validator = {
        'ai_highlights.top_phrases': ['asin', 'phrase', 'count'],
        'ai_highlights.problems': ai_highlights_problems_mapping,
        'ai_highlights.aspects_new2': ai_highlights_aspects_new_mapping,
        'amazon_data.customer_reviews': [
            'review_id', 'product_url', 'asin', 'date', 'country',
            'name', 'title', 'content', 'rating', 'helpful', 'options', 'scrap_datetime',
        ],
    }
    try:
        string = document.decode('latin-1')
        lines = string.splitlines()
        header = lines[0]
        delimiter = None
        for d in [',', ';']:
            if header.count(d):
                delimiter = d
                break
        if not delimiter:
            raise Exception('Invalid delimiter!')
        headmap = header.split(delimiter)
        df = None
        if location in locations_validator:
            if callable(locations_validator[location]):
                df = locations_validator[location](
                    pd.read_csv(StringIO(string), delimiter=delimiter, encoding='latin-1'),
                )
            else:
                for rule in locations_validator[location]:
                    if rule not in headmap:
                        raise Exception('Invalid header!')
        if df is None:
            df = pd.read_csv(StringIO(string), delimiter=delimiter, encoding='latin-1')
    except Exception as e:
        return send_msg(user_id, f'Error occurred: {str(e)}')
    db_col = location.split('.')
    if len(db_col) != 2:
        return send_msg(user_id, f'Collection location is incorrect: {location}')
    db_name, collection = db_col
    try:
        try:
            database.db(db_name)[collection].insert_many(df.T.to_dict().values())
        except Exception:
            database.spec_db(db_name)[collection].insert_many(df.T.to_dict().values())
        return send_msg(user_id, f'Data inserted successfully to {location}!', parse_mode='HTML')
    except Exception as e:
        return send_msg(user_id, f'Error occurred: {str(e)}', parse_mode='HTML')


@cmdreg
def set_category(msg: types.Message, **kwargs):
    text = msg.text.replace('/set_category', '').strip() or None
    if 'cat_group' in kwargs:
        if 'category' in kwargs:
            return _set_category(msg.from_user.id, text, kwargs['category'], kwargs['cat_group'])
        return bot.register_next_step_handler(
            send_msg(msg.from_user.id, 'Enter the ASINs list:'),
            set_category, category=text, cat_group=kwargs['cat_group'],
        )
    return bot.register_next_step_handler(
        send_msg(msg.from_user.id, 'Enter the category name:'),
        set_category, cat_group=text,
    )


def _set_category(user_id, asins, cat_name, cat_group=None):
    if not cat_group:
        cat_group = 'categories'
    data = list([{'Category': cat_name, 'ASIN': asin}
                 for asin in (get_all_asins_from_text(asins) if type(asins) is str else asins)])
    if not data:
        return send_msg(user_id, f'Category is empty')
    try:
        database.db()[cat_group].insert_many(data)
        return send_msg(user_id, f'Category {cat_name} saved to the amazon_data.' + cat_group)
    except Exception as e:
        return send_msg(user_id, f'An error occurred on saving category {cat_name} '
                                 f'to the amazon_data.{cat_group}:\n{e}')


@cmdreg
def rename_category(msg: types.Message, **kwargs):
    text = msg.text.replace('/rename_category', '').strip() or None
    if 'cat_group' in kwargs:
        if 'cat_old' in kwargs:
            return _rename_category(msg.from_user.id, kwargs['cat_old'], text, kwargs['cat_group'])
        return bot.register_next_step_handler(
            send_msg(msg.from_user.id, 'Enter the new name of the category:'),
            rename_category, cat_old=text, cat_group=kwargs['cat_group'],
        )
    return bot.register_next_step_handler(
        send_msg(msg.from_user.id, 'Enter the old category name:'),
        rename_category, cat_group=text,
    )


def _rename_category(user_id, cat_old, cat_new, cat_group=None):
    if not cat_group:
        cat_group = 'categories'
    try:
        database.db()[cat_group].update_many({'Category': cat_old}, {'$set': {'Category': cat_new}})
        return send_msg(user_id, f'Category {cat_old} renamed to {cat_new}')
    except Exception as e:
        return send_msg(user_id, f'An error occurred on renaming category {cat_old} to {cat_new}:\n{e}')


@cmdreg
def delete_asins(msg: types.Message, **kwargs):
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


@cmdreg
def collect_asins_nearby(msg: types.Message, **kwargs):
    asin = msg.text.replace('/collect_asins_nearby', '').strip()
    if asin:
        payload_manager.add_asins_nearby_task(asin, msg.from_user.id, True, kwargs['domain'])
        return send_msg(msg.from_user.id, f'Start finding BSR data [{asin}]')
    return bot.register_next_step_handler(
        send_msg(msg.from_user.id, 'Please enter the ASIN or URL: '),
        collect_asins_nearby, **kwargs,
    )


cmdreg(functools.partial(collect_asins_nearby, domain='amazon.com.mx'), 'collect_asins_nearby_mx')


@cmdreg
def collect_top5(msg: types.Message, **kwargs):
    asin = msg.text.replace('/collect_top5', '').strip()
    if asin:
        payload_manager.add_asins_nearby_task(asin, msg.from_user.id, False, kwargs['domain'])
        return send_msg(msg.from_user.id, f'Start finding BSR data [{asin}]')
    return bot.register_next_step_handler(
        send_msg(msg.from_user.id, 'Please enter the ASIN or URL: '),
        collect_top5, **kwargs,
    )


cmdreg(functools.partial(collect_top5, domain='amazon.com.mx'), 'collect_top5_mx')


@cmdreg
def get_all(msg: types.Message, **kwargs):
    if msg.text == '/get_all':
        return bot.register_next_step_handler(
            send_msg(msg.from_user.id, 'Please enter the ASINs list'),
            get_all, **kwargs,
        )
    if 'asins' not in kwargs:
        asins = get_all_asins_from_text(msg.text)
        if not asins:
            return bot.register_next_step_handler(
                send_msg(msg.from_user.id, f'List name: {msg.text}. Enter the ASINs:'),
                get_all, list=msg.text, **kwargs,
            )
        return bot.register_next_step_handler(
            send_msg(msg.from_user.id, 'Enter the list name:'),
            get_all, asins=asins, **kwargs,
        )
    if 'list' not in kwargs:
        return bot.register_next_step_handler(
            send_msg(msg.from_user.id, 'Enter the collection suffix (or \'-\' sign for defaults):'),
            get_all, list=msg.text, **kwargs,
        )
    collection = 'categories'
    if msg.text != '-':
        collection += '_' + msg.text
    _set_category(msg.from_user.id, kwargs['asins'], kwargs['list'], collection)
    count = len(kwargs['asins']) + 1

    def decrement():
        nonlocal count
        count -= 1
        if not count:
            _export_asins(kwargs['asins'], msg.from_user.id)

    payload_manager.add_products_task(
        kwargs['asins'], kwargs['list'],
        msg.from_user.id, callback=decrement,
        domain=kwargs['domain'],
    )
    payload_manager.add_reviews_tasks(
        kwargs['asins'], msg.from_user.id,
        callback=decrement, domain=kwargs['domain'],
    )


cmdreg(functools.partial(get_all, domain='amazon.com.mx'), 'get_all_mx')


@cmdreg
def update_department_collection(msg: types.Message, **kwargs):
    dep_name = msg.text.replace('/update_department_collection', '').strip()
    payload_manager.add_departments_task(dep_name, msg.from_user.id)
    return send_msg(msg.from_user.id, f'Start collecting departments [{dep_name or "all deps."}]')


def unknown(msg: types.Message, **kwargs):
    return send_msg(msg.from_user.id, 'Unknown command')


def buttons():
    keyboard = types.ReplyKeyboardMarkup()
    for command in CMDs:
        key = types.InlineKeyboardButton(text='/' + command)
        keyboard.add(key)

    return keyboard


@cmdreg
def cmd(msg: types.Message, **kwargs):
    return bot.send_message(msg.from_user.id, 'All commands:\n/' + '\n/'.join(CMDs.keys()), reply_markup=buttons(),
                            parse_mode='HTML')


def non_verification_user_msg(msg: types.Message):
    receive_message(msg)
    if msg.text.strip() == PASSWORD:
        auth_users.add(msg.from_user.id)
        send_msg(msg.from_user.id, 'Login success! You can use all bot functions!')
        return
    send_msg(msg.from_user.id, 'Verification failed. Please enter the master password')


# ##BOTTLE REQUESTS## #
def run_bottle():
    @bottle.route('/send_msg', method='POST')
    def send_message():
        msg = request.forms.get('msg')
        user_id = request.forms.get('uid')
        resp_body = {}
        if request.files:
            resp_body['doc_id'] = []
            for file in request.files:
                try:
                    resp_body['doc_id'].append(bot.send_document(
                        user_id, request.files[file].file,
                        visible_file_name=request.files[file].filename,
                    ).message_id)
                except:
                    pass
        if msg:
            try:
                resp_body['msg_id'] = bot.send_message(user_id, msg).message_id
            except:
                pass
        return bottle.HTTPResponse(status=200, body=json.dumps(resp_body))

    @bottle.route('/edit_msg', method='POST')
    def edit_msg():
        msg_id = request.forms.get('msg_id')
        user_id = request.forms.get('user_id')
        new_text = request.forms.get('msg_text')
        log(msg_id, user_id, new_text)
        try:
            if bot.edit_message_text(new_text, user_id, msg_id):
                return bottle.HTTPResponse(status=204)
            else:
                return bottle.HTTPResponse(status=500)
        except Exception as e:
            return bottle.HTTPResponse(status=500, body=str(e))

    @bottle.route('/end_task', method='POST')
    def end_task():
        _id = request.forms.get('_id')
        try:
            payload_manager.end_task(_id)
            return bottle.HTTPResponse(status=204)
        except KeyError:
            return bottle.HTTPResponse(status=404)
        except:
            return bottle.HTTPResponse(status=500)

    bottle.run(host='0.0.0.0', port=8080, debug=True)


if __name__ == '__main__':
    bot.register_message_handler(callback=non_verification_user_msg, func=lambda msg: not auth(msg))
    bot.register_message_handler(callback=unknown, func=lambda _: True)
    bottle_thr = Thread(target=run_bottle, daemon=True)
    bottle_thr.start()
    if os.path.exists('CHANGELOG'):
        with open('CHANGELOG') as f:
            changelog = f.read()
        os.remove('CHANGELOG')
    else:
        changelog = input('Enter the CHANGELOG: ') or None
    if os.path.exists('auth_users.data'):
        with open('auth_users.data') as f:
            for user in f:
                auth_users.add(int(user))
                bot.send_message(user, 'Hello! Bot is alive!')
                if changelog:
                    bot.send_message(user, 'CHANGELOG:\n' + changelog)
    try:
        bot.infinity_polling()
    finally:
        payload_manager.alive = False
        payload_manager.processes_waiters.shutdown(cancel_futures=True)
        with open('auth_users.data', 'w') as f:
            for user in auth_users:
                f.write(str(user) + '\n')
                bot.send_message(user, 'Bot stopped. We will notify you when the bot is alive')
