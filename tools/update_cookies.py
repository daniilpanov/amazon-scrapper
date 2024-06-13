from functions import base_chrome_init
import db_mongo

sid = []
while cookie := db_mongo.db('amazon_data')['__cookies'].find_one({'session-id': {'$nin': sid}}):
    del cookie['_id']
    wd = base_chrome_init(False, goto='https://amazon.com', user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36', cookies=cookie)
    wd.change_loc()
    wd.full_close()
    sid.append(cookie['session-id'])
