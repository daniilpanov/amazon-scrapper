from functions import base_chrome_init


def init_session(domain='amazon.com'):
    wd = base_chrome_init(f'https://{domain}')
    wd.change_loc()
    wd.execute_script('return {session: cookieStore.get("session-id"), time: cookieStore.get("session-id-time")}')