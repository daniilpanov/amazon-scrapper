import enum
import random
import typing

import names
import requests
from pydantic import BaseModel
from requests import Session, Response
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
        return self.session.request(method, url, **kwargs)

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
        return self.req('POST', 'api/firstDay0')

    def get_all_last_days(self):
        return self.req('POST', 'api/allLastDay')

    def get_configurations(self, config_keys: list[str]):
        """
        {"key": "global.language"},
        {"key": "global.currency"},
        {"key": "global.country"},
        {"key": "contact.qrcode"},
        {"key": "user.telephone"},

        {"key": "global.category.tree"}

        {"key": "video.filter.revenue"},
        {"key": "video.filter.video_type"},
        {"key": "video.filter.creator_followers"},
        {"key": "video.filter.views"},
        {"key": "video.filter.duration"},
        {"key": "video.filter.publish_date"},
        {"key": "video.filter.engagement_rate"},
        {"key": "video.filter.ad.cost"},
        {"key": "video.filter.ad.roas"},
        {"key": "video.filter.ad.view_ratio"},
        {"key": "video.filter.ad.creator_debut"},
        {"key": "video.filter.ad.revenue_ratio"},
        {"key": "livestream.filter.revenue"},
        {"key": "livestream.filter.live_type"},
        {"key": "livestream.filter.creator_followers"},
        {"key": "livestream.filter.unit_price"},
        {"key": "livestream.filter.time_range"},
        {"key": "livestream.filter.live_recorded"},
        {"key": "product.filter.revenue"},
        {"key": "product.filter.affiliate_type"},
        {"key": "product.filter.unit_price"},
        {"key": "product.filter.creator"},
        {"key": "product.filter.sales_channel"},
        {"key": "product.filter.creator_conversion_ratio"},
        {"key": "product.filter.launch_date"},
        {"key": "product.filter.commission_rate"},
        {"key": "creator.filter.revenue"},
        {"key": "creator.filter.creator_type"},
        {"key": "creator.filter.content_type"},
        {"key": "creator.filter.avg_promote_video_views"},
        {"key": "creator.filter.followers"},
        {"key": "creator.filter.avg_normal_video_views"},
        {"key": "creator.filter.engagement_rate"},
        {"key": "creator.filter.creator_content"},
        {"key": "creator.filter.mcn_status"},
        {"key": "creator.filter.ad.creator_debut"},
        {"key": "seller.filter.revenue"},
        {"key": "seller.filter.unit_price"},
        {"key": "seller.filter.seller_type"},
        {"key": "seller.filter.operation_mode"},
        {"key": "global.filter.revenue"},
        {"key": "global.filter.revenue_growth"},
        {"key": "global.filter.average_revenue"},
        {"key": "global.filter.top3_revenue"},
        {"key": "global.filter.top10_revenue"},
        {"key": "global.filter.category_level"},
        {"key": "global.filter.revenue_trend"},
        {"key": "global.filter.is_full_service"},
        {"key": "global.filter.delivery_type"},
        """
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

    def get_user_features(self):
        return self.req('POST', 'user/features', json={
            'country': 'US',
            'list': [
                'OVERVIEW.POTENTIAL_LIST',
                'OVERVIEW.DETAIL',
                'OVERVIEW.LEVEL_THIRD',
                'OVERVIEW.DATA_RANGE',
                'VIDEO.LIST',
                'VIDEO.DETAIL',
                'LIVESTREAM.LIST',
                'LIVESTREAM.DETAIL',
                'PRODUCT.LIST',
                'PRODUCT.DETAIL',
                'CREATOR.LIST',
                'DATA.EXPORT',
                'CREATOR.DETAIL',
                'CREATOR.MCN_SIGN',
                'CREATOR.CONTACT',
                'CREATOR.COLLABORATED_SHOP',
                'FORYOU.TABLELIST',
                'FORYOU.COLLABORATED_SHOP',
                'FORYOU.HOT',
                'FORYOU.FOCUSCOUNT',
                'SHOP.LIST',
                'SHOP.DETAIL',
                'DOWNLOAD.VIDEO',
                'FILTER.CUSTOM_RANGE',
                'LIST.DATE_RANGE',
                'DETAIL.DATE_RANGE',
                'LIST.DATE_SPACING',
                'DETAIL.DATE_SPACING',
                'LIVESTREAM.FULL_RECORD',
                'LIST.CATE_CASCADER_LIST',
                'FILTER.CUSTOM_TIMES',
                'AD.ANALYSIS',
                'AD.CREATOR_DEBUT',
                'DETAIL.ACCESS_TIMES',
                'CUSTOMIZED.DATA.EXPORT',
            ],
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
            'scene': email_checker.scene,
            'email': email_checker.email,
            'captchaType': email_checker.captchaType,
        })

    def verify_email_message(self, email_checker: EmailChecker):
        return self.req('POST', 'email/check' + email_checker.scene.title() + 'Verification', json={
            "email": email_checker.email,
            "loginMethod": "EMAIL",
            "emailCode": email_checker.code,
            "scene": email_checker.scene,
        },
                        )

    def singup_or_login(self, email_checker: EmailChecker):
        return self.req('POST', 'user/' + email_checker.scene, json={
            "scene": email_checker.scene,
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


class Creator(Request, BaseModel):
    id: str
    nickname: str | None = None
    revenue: float | None = None
    live_revenue: float | None = None
    video_revenue: float | None = None
    sale: float | None = None
    followers: int | None = None

    def __init__(self, _id: str, req: Request):
        super().__init__(req)
        self.id = _id


class Product(Request, BaseModel):
    id: str
    conversion_ratio: float | None = None
    creators_count: int | None = None
    related_creators: list[Creator] = []
    metrics: dict[str, float] = {}

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

    def get_conversion_ratio(self):
        res = self.get_json_data(self.req('POST', 'product/detail/creator/getConversionRadio', json={
            "id": self.id,
            "startDate": self.start_date,
            "endDate": self.end_date,
        }))
        self.creators_count = res.get('creatorNum')
        self.creators_count = res.get('creatorConversionRatio')

    def get_creators(self, page: int, psize: int = 10):
        return self.get_json_data(self.req('POST', 'product/detail/creator/queryList', json={
            "id": self.id,
            "startDate": self.start_date,
            "endDate": self.end_date,
            "authority": True,
            "pageNo": page,
            "pageSize": psize,
            "sort": [
                {
                    "field": "revenue",
                    "type": "DESC"
                },
            ],
        }))
