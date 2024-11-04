import enum
import random

import names
import pydantic
import requests
from requests import Session


class CheckEmailScene(enum.StrEnum):
    SIGNUP = 'signup'
    LOGIN = 'login'


class EmailChecker(pydantic.BaseModel):
    response: str
    scene: CheckEmailScene
    email: str
    captchaType: str


class Kalodata:
    base_url = 'https://www.kalodata.com/'
    default_headers = {

    }
    session: Session
    # country = 'US'
    # currency = 'USD'

    def __init__(self):
        self.session = requests.session()

    def init(self):
        pass

    def query_profile(self):
        pass

    def get_first_day(self):
        pass

    def get_all_last_days(self):
        pass

    def get_configurations(self, config_keys):
        pass

    def homepage_dialog_query_list(self):
        pass

    def user_query_membership(self):
        pass

    def get_country_contacts(self):
        pass

    def get_user_features(self):
        pass

    def livestream_query_unwatch(self):
        pass

    def logout(self):
        pass

    def send_email_message(self, scene: CheckEmailScene, email: str, response: str = 'token', captchaType: str = 'cloudflare') -> EmailChecker:
        pass

    def verify_email_message(self, email_checker: EmailChecker, code: str):
        pass

    def search_user_tc_code(self):  # unknown
        pass

    def get_homepage_banners_query_list(self):
        pass

    def get_homepage_solution_query_list(self):
        pass

    def overview_rank_query_products_tops(self, start_date: str, end_date: str, page_num: int, page_size: int):
        pass

    def overview_rank_query_creators_tops(self, start_date: str, end_date: str, page_num: int, page_size: int):
        pass

    def overview_rank_query_shops_tops(self, start_date: str, end_date: str, page_num: int, page_size: int):
        pass

    def overview_rank_query_video_tops(self, start_date: str, end_date: str, page_num: int, page_size: int):
        pass

    def overview_rank_query_live_tops(self, start_date: str, end_date: str, page_num: int, page_size: int):
        pass

    def creator_enrich(self, start_date: str, end_date: str, page_num: int, page_size: int):
        pass

    def shop_enrich(self, start_date: str, end_date: str, page_num: int, page_size: int):
        pass

    def video_enrich(self, start_date: str, end_date: str, page_num: int, page_size: int):
        pass

    def livestream_enrich(self, start_date: str, end_date: str, page_num: int, page_size: int):
        pass

    def modify_profile(self, **data):
        r = self.session.post(
            self.base_url + 'user/modifyProfile',
            json=data,
        )

    def modify_profile_initially(self, **data):
        defaults = {
            'businessOnTiktok': 'No',
            'identity': 'None of the above',
            'companySize': '1-5',
            'firstName': names.get_first_name(),
            'lastName': (random.randint(0, 1) and names.get_last_name() or ''),
        }
        return self.modify_profile(**defaults, **data)

    def modify_profile_source(self, source='Others'):
        return self.modify_profile(source=source)
