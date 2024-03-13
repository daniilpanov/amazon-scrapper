import random

import aiohttp
from random_user_agent.params import SoftwareName, OperatingSystem
from random_user_agent.user_agent import UserAgent

from functions import base_chrome_init


class Requests:
    request: aiohttp.ClientSession
    cookies: dict | None = None
    reviews_request_counter: int = 1
    domain: str

    def __init__(self, domain='amazon.com', **kwargs):
        self.domain = domain
        if 'session-id' in kwargs and 'session-id-time' in kwargs:
            self.cookies = {'session-id-time': kwargs['session-id-time'], 'session-id': kwargs['session-id']}
        elif Requests.cookies:
            self.cookies = Requests.cookies
        else:
            #
            wd = base_chrome_init(goto=f'https://{domain}')
            wd.change_loc()
            #
            cookies = wd.get_cookies()
            wd.quit()
            Requests.cookies = {}
            for cookie in cookies:
                Requests.cookies[cookie['name']] = cookie['value']
            self.cookies = Requests.cookies
            self.request = aiohttp.ClientSession(cookies=self.cookies)

    async def req(self, path='', method='GET', params=None, headers=None, xmlhttp=False, ref=None):
        return await self.request.request(method, f'https://{self.domain}/{path}', params=params, headers={
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
            'X-Requested-With': 'XMLHttpRequest',
            'Sec-Ch-Dpr': '1.25',
            'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': 'Windows',
            'Sec-Ch-Ua-Platform-Version': '14.0.0',
            'Sec-Ch-Viewport-Width': '810',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Viewport-Width': '810',
        } if xmlhttp else {}) | (headers or {}))

    async def get_html(self, path='', headers=None):
        res = await self.req(path, headers=headers)
        if res.status == 200:
            return await res.text()
        return None

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
        if res.status == 200:
            self.reviews_request_counter += 1
            return await res.text()
        print('FAIL:', res, await res.text())
        return None
