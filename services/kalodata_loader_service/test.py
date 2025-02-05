import time

import logging

# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)

try:
    from .kalodata_requests import *
except ImportError:
    from kalodata_requests import *


def log_request(p, r):
    print('------')
    print(p)
    print(r, r.status_code, r.request.headers, str(r.headers), str(r.cookies.items()), str(r.reason))
    try:
        print(r.json())
    except:
        print(r.text)
    print('------')


kd = Kalodata()
kd.init()
kd.current_page = 'signup'
time.sleep(2)
ec = EmailChecker(CheckEmailScene.SIGNUP)
kd.send_email_message(ec)
c = 0
while True:
    try:
        if ec.get_code():
            break
    except Exception:
        pass
    time.sleep(5)
    c += 5
    if c >= 60:
        kd.send_email_message(ec)
        c = 0
log_request(3, kd.singup_or_login(ec))
kd.verify_email_message(ec)
# time.sleep(1)
# log_request(3.1, kd.singup_or_login(ec))
# time.sleep(1)
# log_request(3.2, kd.singup_or_login(ec))
# log_request(4, kd.modify_profile_initially())
# log_request(5, kd.modify_profile_source())
# log_request(6, kd.modify_profile_password())
