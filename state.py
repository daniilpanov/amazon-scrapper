from threading import Thread, Event
from time import sleep

from database import db


def updating_process(ev: Event):
    while True:
        ev.wait()
        values = values_for_setup.copy()
        values_for_setup.clear()
        for key in values:
            value = int(values[key])
            asin, _type = key.split('_', 1)
            if value >= 959:
                value = -1
            db()['__state'].update_one({'type': _type, 'asin': asin}, {'$set': {'state': value}}, True)
        ev.clear()


def chunk(s, w=10):
    s = s.replace('\n', '').replace(' ', '').replace(',', '').replace('.', '').strip()
    return set([s[i:i + w] for i in range(0, len(s), w)])


def get_asin(asin, _type='reviews'):
    return int((db()['__state'].find_one({'type': _type, 'asin': asin}) or {'state': False})['state'])


def write_asin(asin, value, _type='reviews'):
    global values_for_setup
    values_for_setup[asin + '_' + _type] = value
    update_event.set()


values_for_setup = {}
update_event = Event()
updating_thr = Thread(target=updating_process, args=(update_event,), daemon=True)
updating_thr.start()
