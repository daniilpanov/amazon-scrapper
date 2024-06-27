import random

import requests

import QtWebView
import parser


class ProductCardScene(QtWebView.Scraper):
    asin: str | None = None
    url: str | None = None
    collect_aspects: bool = True
    collect_media_config: bool = False
    target: bool = False

    def __init__(self):
        super(ProductCardScene, self).__init__()

    def beginScene(self, task):
        super().beginScene(task)
        self.task = task
        data = task.get('data', {})
        self.asin = data['asin']
        self.url = ('https://www.' + data.get('domain', 'amazon.com') + '/' + (
            data['canonical_prefix'] + '/' if 'canonical_prefix' in data else '') + '/dp/' + data['asin']
                    + '/ref=sr_1_' + str(random.randint(1, 6)))
        self.collect_aspects = data.get('collect_aspects', True)
        self.collect_media_config = data.get('collect_media_config', False)
        self.target = data.get('target', self.collect_media_config)

    def __next__(self):
        super().__iter__()
        self.setUrl(self.url)
        print('setUrl')

    def actionHtmlLoaded(self, html):
        if not super().actionHtmlLoaded(html):
            return False
        if self.setAmazonLocation():
            return False
        print('load data')
        product_card = parser.parse_product(self.asin, self.soup)
        product_card_json = dict(zip((
                             'asin', 'product_url', 'canonical_prefix', 'product_title', 'product_descr', 'picture_url', 'features', 'top_5_phrases', 'product_price'), product_card))
        if self.collect_aspects:
            aspects = parser.parse_aspects(self.asin, self.soup)
            if aspects:
                aspects_json = [dict(zip(('Aspect', 'positive', 'negative'), aspect)) for aspect in aspects]
                requests.post('http://localhost:8832/products/set_result/aspects/' + self.asin, json=aspects_json)
        if self.collect_media_config:
            media_data = parser.parse_media_links(self.soup)
            if media_data:
                product_card_json['media_data'] = media_data
        else:
            media_data = None
        requests.post('http://localhost:8832/products/set_result/card/' + self.asin, json=product_card_json)

        if media_data and self.target:
            requests.post('http://localhost:8832/products/target/collect/' + self.asin)

        # exit
        if self.task.get('stage') == 1:
            self.set_stage_res_signal.emit(self.task['_id'], 3, {'prefix': product_card_json.get('canonical_prefix')})
            return True
        self.success_signal.emit(self.task['_id'])
        return True

