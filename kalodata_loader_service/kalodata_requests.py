import enum
import random
import typing

import names
import requests
from requests import Session, Response
try:
    from .tempmail import TempMail
except ImportError:
    from tempmail import TempMail


def convert_num(num: str):
    num = num.strip()
    number_range = num.split('-')
    if len(number_range) > 2:
        parts = []
        symbol = None
        for num_part in number_range:
            res = convert_num(num_part)
            symbol = res[0] or symbol
            parts.append(str(res[1]))
        return [symbol, *parts]
    num = num.replace(',', '')
    # Config
    k = 1
    symbols_map = {
        'K': 1000,
        'M': 1000000,
        'B': 1000000000,
    }
    for sym in symbols_map:
        if num[-1].lower() == sym.lower():
            k = symbols_map[sym]
            num = num[:-1]
            break
    symbol = None
    if not num[0].isdigit():
        symbol = num[0]
        num = num[1:]
    elif not num[-1].isdigit():
        symbol = num[-1]
        num = num[:-1]
    try:
        num = float(num)
        return symbol, num * k
    except TypeError:
        return None, None, None


class CheckEmailScene(enum.StrEnum):
    SIGNUP = 'signup'
    LOGIN = 'login'


class Items(enum.StrEnum):
    VIDEO = 'video'
    PRODUCT = 'product'
    CREATOR = 'creator'
    SHOP = 'shop'


class LimitReached(Exception):
    pass


class EmailChecker:
    response: str
    scene: CheckEmailScene
    email: str
    captchaType: str

    tempMailInst: TempMail | None = None
    code: str | None = None

    def __init__(self, scene: CheckEmailScene, captcha_type='cloudflare', response='token'):
        inst = self.tempMailInst = TempMail()
        inst.gen_email()
        self.email = inst.email
        self.scene = scene
        self.captchaType = captcha_type
        self.response = response

    def get_code(self):
        msgs = self.tempMailInst.fetch_emails('noreply@email.kalodata.com')
        for msg in (msgs or []):
            body_parts = msg.fetch_data().get('body', '').split(' ')
            for part in body_parts:
                part = part.strip()
                if not part:
                    continue
                if part.isdigit() and len(part) == 6:
                    self.code = part
                    return part
        return None


class Request:
    host = 'www.kalodata.com'
    base_url = 'https://' + host + '/'
    default_headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-GB,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,en-US;q=0.6',
        'country': 'US',
        'currency': 'USD',
        'dnt': '1',
        'language': 'en-US',
        'host': host,
        'origin': base_url,
        'priority': 'u=1, i',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    }
    current_page = ''
    session: Session
    start_date: str | None = None
    end_date: str | None = None

    def __init__(self, req: typing.Self | None = None):
        if req:
            self.session = req.session
            self.start_date = req.start_date
            self.end_date = req.end_date
        else:
            self.session = requests.session()
            self.session.headers.update(self.default_headers)

    def req(self, method, url, **kwargs):
        kwargs['headers'] = {'referer': self.base_url + self.current_page} | kwargs.get('headers', {})
        return self.session.request(method, self.base_url + url, **kwargs)

    def get_text_data(self, req: Response):
        if req.status_code > 299:
            raise LimitReached
        return req.text

    def get_json_data(self, req: Response):
        if req.status_code > 299:
            raise LimitReached
        data = req.json()
        if not data or not data.get('success'):
            raise LimitReached
        return data.get('data')


class Kalodata(Request):
    def init(self):
        return self.session.get(self.base_url, headers={
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1'
        })

    def query_profile(self):
        return self.req('POST', 'user/queryProfile')

    def get_first_day(self):
        return self.req('POST', 'api/firstDay0', json={'country': 'US'})

    def get_all_last_days(self):
        return self.req('GET', 'api/allLastDay')

    def get_configurations(self, config_keys: list[str]):
        data = []
        for key in config_keys:
            data.append({'key': key})
        return self.req('POST', 'api/configurations', json=data)

    def homepage_dialog_query_list(self):
        return self.req('POST', 'homepage/dialog/queryList')

    def user_query_membership(self):
        return self.req('POST', 'user/queryMembership', json={'country': 'US'})

    def get_country_contacts(self):
        return self.req('POST', 'v1/countryV1/contacts', params={'type': 'pc'}, headers={
            'origin': None,
            'content-type': None,
        })

    def get_user_features(self, lst):
        return self.req('POST', 'user/features', json={
            'country': 'US',
            'list': lst,
        })

    def livestream_query_unwatch(self):
        return self.req('POST', 'livestream/queryUnWatch', headers={
            'content-type': None,
        })

    def logout(self):
        return self.req('POST', 'user/logout', headers={
            'content-type': None,
        })

    def send_email_message(self, email_checker: EmailChecker):
        return self.req('POST', 'email/emailSendMessage', json={
            'response': email_checker.response,
            'scene': str(email_checker.scene),
            'email': email_checker.email,
            'captchaType': email_checker.captchaType,
        })

    def verify_email_message(self, email_checker: EmailChecker):
        return self.req('POST', 'email/check' + email_checker.scene.title() + 'Verification', json={
            "email": email_checker.email,
            "loginMethod": "EMAIL",
            "emailCode": email_checker.code,
            "scene": str(email_checker.scene),
        })

    def singup_or_login(self, email_checker: EmailChecker, scene_key: str | None = None):
        # It's just kalodata bug :) wrong key 'scence' on signing up
        key_scene = scene_key or ('scene' if email_checker.scene is CheckEmailScene.LOGIN else 'scence')
        print({
            str(key_scene): str(email_checker.scene),
            "tcCode": "",
            "email": email_checker.email,
            "emailCode": email_checker.code,
            "loginMethod": "EMAIL",
        })
        return self.req('POST', 'user/' + email_checker.scene, json={
            str(key_scene): str(email_checker.scene),
            "tcCode": "",
            "email": email_checker.email,
            "emailCode": email_checker.code,
            "loginMethod": "EMAIL",
        })

    def search_user_tc_code(self, email_checker: EmailChecker):  # unknown
        return self.req('POST', 'user/searchUserTCCode', json={
            "email": email_checker.email,
        })

    def homepage_banners_query_list(self):
        return self.req('POST', 'homepage/banner/queryList', headers={
            'content-type': None,
        })

    def homepage_solution_query_list(self):
        return self.req('POST', 'homepage/solution/queryList', headers={
            'content-type': None,
        })

    def modify_profile(self, **data):
        return self.session.post(
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

    def modify_profile_password(self, passwd='OsdKey0909'):
        return self.modify_profile(passwd=passwd)

    # THE MOST IMPORTANT:
    def overview_rank_query_products_tops(self, page_num: int, page_size: int = 10):
        return self.req('POST', 'overview/rank/queryProductTops', json={
            "startDate": self.start_date,
            "endDate": self.end_date,
            "pageNo": page_num,
            "pageSize": page_size,
        })

    def overview_rank_query_creators_tops(self, page_num: int, page_size: int = 10):
        return self.req('POST', 'overview/rank/queryCreatorTops', json={
            "startDate": self.start_date,
            "endDate": self.end_date,
            "pageNo": page_num,
            "pageSize": page_size,
        })

    def overview_rank_query_shops_tops(self, page_num: int, page_size: int = 10):
        return self.req('POST', 'overview/rank/queryShopTops', json={
            "startDate": self.start_date,
            "endDate": self.end_date,
            "pageNo": page_num,
            "pageSize": page_size,
        })

    def overview_rank_query_video_tops(self, page_num: int, page_size: int = 10):
        return self.req('POST', 'overview/rank/queryVideoTops', json={
            "startDate": self.start_date,
            "endDate": self.end_date,
            "pageNo": page_num,
            "pageSize": page_size,
        })

    def overview_rank_query_live_tops(self, page_num: int, page_size: int = 10):
        return self.req('POST', 'overview/rank/queryLiveTops', json={
            "startDate": self.start_date,
            "endDate": self.end_date,
            "pageNo": page_num,
            "pageSize": page_size,
        })

    def creator_enrich(self, ids: list[str], cate_ids: list[str] | None = None):
        return self.req('POST', 'creator/enrich', json={
            "ids": ids,
            "country": "US",
            "startDate": self.start_date,
            "endDate": self.end_date,
            "cateIds": cate_ids or [],
        })

    def shop_enrich(self, ids: list[str], cate_ids: list[str] | None = None):
        return self.req('POST', 'shop/enrich', json={
            "ids": ids,
            "country": "US",
            "startDate": self.start_date,
            "endDate": self.end_date,
            "cateIds": cate_ids or [],
        })

    def video_enrich(self, ids: list[str], cate_ids: list[str] | None = None):
        return self.req('POST', 'video/enrich', json={
            "ids": ids,
            "country": "US",
            "startDate": self.start_date,
            "endDate": self.end_date,
            "cateIds": cate_ids or [],
        })

    def livestream_enrich(self, ids: list[str], cate_ids: list[str] | None = None):
        return self.req('POST', 'livestream/enrich', json={
            "ids": ids,
            "country": "US",
            "startDate": self.start_date,
            "endDate": self.end_date,
            "cateIds": cate_ids or [],
        })


class KalodataController:
    kalodata_inst: Kalodata
    
    def __init__(self):
        self.kalodata_inst = Kalodata()
        
    def initialize(self):
        self.kalodata_inst.init()
        self.kalodata_inst.start_date = self.kalodata_inst.get_json_data(self.kalodata_inst.get_first_day())
        last_days = self.kalodata_inst.get_json_data(self.kalodata_inst.get_all_last_days())
        for country, date in last_days.items():
            if country == 'US':
                self.kalodata_inst.end_date = date
                break


class Creator(Request):
    id: str
    nickname: str | None = None
    revenue: float | None = None
    live_revenue: float | None = None
    video_revenue: float | None = None
    sale: float | None = None
    followers: int | None = None
    count_coop_shops: int | None = None
    history: list[dict] = []
    metrics: dict[str, float] = {}
    contacts: dict[str, str] = {}
    collect_date: str | None = None
    creator_type: str | None = None
    creator_debut: str | None = None
    seller_id: str | None = None
    products_count: int | None = None
    region: str | None = None
    main_categories: dict[str, str | None] = {}
    categories: dict[str, list | None] = {}

    def __init__(self, _id: str, req: Request):
        super().__init__(req)
        self.id = _id

    def search_shop_list(self):
        return self.get_json_data(self.req('POST', 'creator/detail/searchShopList', json={
            "authority": True,
            "id": self.id,
            "startDate": self.start_date,
            "endDate": self.end_date,
        }))

    def count_cooperative_shops(self, page=1, psize=10):
        self.count_coop_shops = self.get_json_data(self.req('POST', 'creator/detail/searchCooperativeShops/count', json={
            "id": self.id,
            "startDate": self.start_date,
            "endDate": self.end_date,
            "authority": True,
            "pageNo": page,
            "pageSize": psize,
            "sort": [
                {
                    "field": "revenue",
                    "type": "DESC",
                },
            ],
        }))

    def search_cooperative_shops(self, page=1, psize=10):
        return self.get_json_data(self.req('POST', 'creator/detail/searchCooperativeShops', json={
            "id": self.id,
            "startDate": self.start_date,
            "endDate": self.end_date,
            "authority": True,
            "pageNo": page,
            "pageSize": psize,
            "sort": [
                {
                    "field": "revenue",
                    "type": "DESC",
                },
            ],
        }))

    def search_products(self, page=1, psize=10):
        return self.get_json_data(self.req('POST', 'creator/detail/searchProducts', json={
            "id": self.id,
            "startDate": self.start_date,
            "endDate": self.end_date,
            "authority": True,
            "pageNo": page,
            "pageSize": psize,
            "sort": [
                {
                    "field": "revenue",
                    "type": "DESC",
                },
            ],
        }))

    def get_history(self):
        return self.get_json_data(self.req('POST', 'creator/detail/history/total', json={
            "id": self.id,
            "startDate": self.start_date,
            "endDate": self.end_date,            "authority": True,
            "cateIds": [],
            "sellerId": "",
        }))

    def get_metrics(self):
        res = self.get_json_data(self.req('POST', 'creator/detail/total', json={
            "id": self.id,
            "startDate": self.start_date,
            "endDate": self.end_date,
            "authority": True,
            "cateIds": [],
            "sellerId": "",
        }))
        for key, val in res.items():
            self.metrics[key] = convert_num(val)[1]

    def get_details(self):
        details = self.get_json_data(self.req('POST', 'creator/detail', json={
            "id": self.id,
            "startDate": self.start_date,
            "endDate": self.end_date,
            "authority": True,
            "cateIds": [],
            "sellerId": "",
        })) or {}
        self.contacts = {key: (val or None) for key, val in details.get('creatorContent', {}).items()}
        self.collect_date = details.get('collect_day')
        self.creator_type = details.get('creator_type')
        self.creator_debut = details.get('creatorDebut')
        self.seller_id = details.get('seller_id')
        self.nickname = details.get('nickname')
        self.products_count = int(details.get('products_count', 0))
        self.region = details.get('region')
        self.main_categories = details.get('main_category')
        self.categories = {
            'pri': details.get('pri_cate_ids'),
            'sec': details.get('sec_cate_ids'),
            'ter': details.get('ter_cate_ids'),
        }


class Product(Request):
    id: str
    conversion_ratio: float | None = None
    creators_count: int | None = None
    related_creators: list[Creator] = []
    metrics: dict[str, float] = {}
    history: list[dict] = []
    seller_id: str | None = None
    title: str | None = None
    prices: dict[str, float] = {}
    is_affiliate: bool | None = None
    is_full_service: bool | None = None
    collect_date: str | None = None
    commission_rate: str | None = None
    creator_gmv_concentration: float | None = None
    brand_name: str | None = None

    def __init__(self, _id: str, req: Request):
        super().__init__(req)
        self.id = _id

    def get_metrics(self):
        res = self.get_json_data(self.req('POST', 'product/detail/total', json={
            "authority": True,
            "id": self.id,
            "startDate": self.start_date,
            "endDate": self.end_date,
        }))
        for key, val in res.items():
            self.metrics[key] = convert_num(val)[1]

    def get_history(self):
        self.history = self.get_json_data(self.req('POST', 'product/detail/history', json={
            "authority": True,
            "id": self.id,
            "startDate": self.start_date,
            "endDate": self.end_date,
        }))

    def get_details(self):
        details = self.get_json_data(self.req('POST', 'product/detail', json={
            "authority": True,
            "id": self.id,
            "startDate": self.start_date,
            "endDate": self.end_date,
        }))
        self.seller_id = details.get('seller_id') or None
        self.title = details.get('product_title') or None
        self.prices = {
            'max_original_price': details.get('max_original_price') or None,
            'max_real_price': details.get('max_real_price') or None,
            'min_in_30_price': details.get('min_in_30_price') or None,
            'min_original_price': details.get('min_original_price') or None,
            'min_real_price': details.get('min_real_price') or None,
            'unit_price': details.get('unit_price') or None,
        }
        self.is_affiliate = details.get('is_affiliate')
        if self.is_affiliate is not None:
            self.is_affiliate = bool(self.is_affiliate)
        self.is_full_service = details.get('is_full_service')
        if self.is_full_service is not None:
            self.is_full_service = bool(self.is_full_service)
        self.collect_date = details.get('collect_day') or None
        self.commission_rate = details.get('commission_rate') or None
        if self.commission_rate == '-':
            self.commission_rate = None
        self.creator_gmv_concentration = details.get('creator_gmv_concentration') or None
        self.brand_name = details.get('brand_name') or None

    def get_conversion_ratio(self):
        res = self.get_json_data(self.req('POST', 'product/detail/creator/getConversionRadio', json={
            "id": self.id,
            "startDate": self.start_date,
            "endDate": self.end_date,
        }))
        self.creators_count = res.get('creatorNum')
        self.creators_count = res.get('creatorConversionRatio')

    def get_items(self, item: Items, page: int, psize: int = 10):
        return self.get_json_data(self.req('POST', 'product/detail/' + item + '/queryList', json={
            "id": self.id,
            "startDate": self.start_date,
            "endDate": self.end_date,
            "authority": True,
            "pageNo": page,
            "pageSize": psize,
            "sort": [
                {
                    "field": "revenue",
                    "type": "DESC",
                },
            ],
        }))

    def count_related(self, item: Items, page=1, psize=10):
        return self.get_json_data(self.req('POST', 'product/detail/' + item + '/count', json={
            "id": self.id,
            "startDate": self.start_date,
            "endDate": self.end_date,
            "authority": True,
            "pageNo": page,
            "pageSize": psize,
            "sort": [
                {
                    "field": "revenue",
                    "type": "DESC",
                },
            ],
        }))
