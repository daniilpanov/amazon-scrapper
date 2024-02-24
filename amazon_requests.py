import requests

from functions import base_chrome_init


class Requests:
    request: requests.Session
    reviews_request_counter: int = 1

    def __init__(self, domain='amazon.com'):
        #
        wd = base_chrome_init(goto=f'https://{domain}')
        wd.change_loc()
        #
        cookies = wd.get_cookies()
        wd.quit()
        #
        self.request = requests.Session()
        for cookie in cookies:
            self.request.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'], path=cookie['path'])

    def req(self, path='', method='GET', params=None, cookies=None, headers=None, domain='amazon.com', xmlhttp=False, ref=None):
        return self.request.request(
            method, f'https://{domain}/{path}', params=params or {}, cookies=cookies or {},
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/121.0.0.0 Safari/537.36',
                'Access-Control-Allow-Origin': '*', 'Origin': f'https://{domain}',
                'Referer': ref or f'https://{domain}/',
            } | ({
                'Rtt': '100', 'Sec-Ch-Device-Memory': '8', 'X-Requested-With': 'XMLHttpRequest',
                'Sec-Ch-Dpr': '1.25', 'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
                'Sec-Ch-Ua-Mobile': '?0', 'Sec-Ch-Ua-Platform': 'Windows',
                'Sec-Ch-Ua-Platform-Version': '14.0.0', 'Sec-Ch-Viewport-Width': '810',
                'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin', 'Viewport-Width': '810',
            } if xmlhttp else {}) | (headers or {}),
        )

    def get_html(self, path='', cookies=None, headers=None, domain='amazon.com'):
        res = self.req(path, cookies=cookies, headers=headers, domain=domain)
        if res.status_code == 200:
            return res.text
        return None

    def get_reviews(self, asin, page=1, params=None, keywords='', **kwargs):
        curr_params = {
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
        res = self.req(kwargs.get('canonical_link', f'/product-reviews/{asin}'), 'GET', params, domain=kwargs.get('domain', 'amazon.com'))
        # res = self.req('/hz/reviews-render/ajax/reviews/get/ref=cm_cr_arp_d_viewopt_srt', 'POST', params, domain=kwargs.get('domain', 'amazon.com'), xmlhttp=True)
        if res.status_code == 200:
            self.reviews_request_counter += 1
            return res.text
        print('FAIL:', res, res.text)
        return None

