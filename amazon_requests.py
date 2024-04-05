import random

import aiohttp
from random_user_agent.params import SoftwareName, OperatingSystem
from random_user_agent.user_agent import UserAgent

import settings
from database import db


class Requests:
    request: aiohttp.ClientSession | None = None
    reviews_request_counter: int = 1
    domain: str
    all_cookies = None
    sessid: str | None = None
    proxy: str | None = None

    def __new__(cls, domain='amazon.com'):
        if not cls.all_cookies:
            cls.all_cookies = {i['session-id']: i for i in db('amazon_data')['__cookies'].find()}
        inst = super(Requests, cls).__new__(cls)
        inst.domain = domain
        return inst

    async def init(self, retry=True, proxy=None):
        if self.request:
            await self.request.close()
        if Requests.all_cookies:
            cookies = random.choice(list(Requests.all_cookies.values()))
            self.sessid = cookies.get('session-id')
        else:
            cookies = {}
        self.proxy = proxy or settings.PROXY
        self.request = aiohttp.ClientSession(cookies=cookies)
        await self.req(retry=retry)

    async def req(self, path='', method='GET', params=None, headers=None, xmlhttp=False, ref=None, abs_path=False, retry=True):
        try:
            url = path if abs_path else f'https://{self.domain}/{path}'
            return await self.request.request(method, url, proxy=self.proxy, params=params, headers={
                'User-Agent': UserAgent(
                    100, software_names=[SoftwareName.CHROME.value],
                    operating_systems=[OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value],
                ).get_random_user_agent(),
                'Access-Control-Allow-Origin': '*',
                'Origin': f'https://{self.domain}',
                'Referer': ref or f'https://{self.domain}/',
            } | ({
                'Rtt': '100',
                'Sec-Ch-Device-Memory': '8',
                'Sec-Ch-Dpr': '1.25',
                'Sec-Ch-Ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': 'Windows',
                'Sec-Ch-Ua-Platform-Version': '14.0.0',
                'Sec-Ch-Viewport-Width': '810',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'Viewport-Width': '810',
                'X-Requested-With': 'XMLHttpRequest',
            } if xmlhttp else {}) | (headers or {}))
        except Exception:
            if not retry:
                return None
            await self.init(False)
            return await self.req(path, method, params, headers, xmlhttp, ref, abs_path, False)

    async def get_html(self, path='', headers=None, abs_path=False):
        res = await self.req(path, headers=headers, abs_path=abs_path)
        if res and res.status == 200:
            return await res.text()
        return None

    @staticmethod
    def check_captcha(soup):
        return bool(soup.select('body > div > div[style*="width: 350px"]'))

    async def get_reviews(self, asin, page=1, params=None, keywords='', xmlhttp=True, **kwargs):
        curr_params = {
            'formatType': 'current_format' if kwargs.get('current_format') else '',
            'filterByAge': '',
            'pageNumber': page,
            'filterByLanguage': '',
            'filterByKeyword': keywords,
            'shouldAppend': 'undefined',
            'deviceType': 'desktop',
            'canShowIntHeader': 'undefined',
            'reftag': 'cm_cr_arp_d_viewopt_srt',
            'pageSize': 10,
            'asin': asin,
            'scope': 'reviewsAjax{}'.format(self.reviews_request_counter),
        }
        if not params:
            params = {}
        params |= curr_params
        if xmlhttp:
            res = await self.req(
                'hz/reviews-render/ajax/reviews/get/ref=cm_cr_arp_d_viewopt_srt',
                'POST', params, xmlhttp=True,
            )
        else:
            res = await self.req(kwargs.get('canonical_link', f'product-reviews/{asin}'), 'GET', params)
        if res and res.status == 200:
            self.reviews_request_counter += 1
            return await res.text()
        # print('FAIL:', res)
        return None
