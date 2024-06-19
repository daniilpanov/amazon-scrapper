import datetime
import re

import orjson
import pytz
from bs4 import BeautifulSoup

from amazon_requests import Requests


def month_to_int(month: str):
    month = month.lower()
    if month[0] == 'f':
        r = 2
    elif month[0] == 'j' and month[1] == 'u':
        r = 6 + ('l' in month)
    elif month[0] == 'a':
        r = 4 + 4 * ('g' in month)
    elif month[0] == 'm':
        r = 3 + 2 * ('r' not in month)
    elif month[0] == 's':
        r = 9
    elif month[0] == 'o':
        r = 10
    elif month[0] == 'n':
        r = 11
    elif month[0] == 'd':
        r = 12
    else:
        r = 1
    return r


def parse_reviews(asin, html, domain='amazon.com'):
    if type(html) is not str:
        item_parser = html
        review_id = html['id']
    else:
        item_parser = BeautifulSoup(html, features='lxml')
        if not item_parser or not item_parser.find(attrs={'data-hook': 'review'}) \
                or item_parser.find('div', class_='a-divider-section') \
                or item_parser.find('h3', attrs={'data-hook': 'dp-global-reviews-header'}):
            return False
        review_id = item_parser.find('div', attrs={'data-hook': 'review'})['id']
    # Country & Date
    review_date_raw = item_parser.find('span', attrs={'data-hook': 'review-date'})
    if review_date_raw:
        review_date_words = review_date_raw.text.strip().split(' ')
        # parse date and country
        first = True
        review_country = ''
        idx = 0
        for word in review_date_words:
            if word.istitle():
                if first:
                    first = False
                else:
                    review_country += word + ' '
            elif review_country:
                review_country = review_country.strip()
                idx += 1
                break
            idx += 1
        date_part = [rword.replace(',', '') for rword in review_date_words[idx:]]
        year_like = list(filter(lambda x: x.isdigit() and len(x) == 4, date_part))
        review_date_dict: dict[str, int | None] = {}
        if len(year_like) == 1:
            review_date_dict['year'] = int(year_like[0])
        else:
            review_date_dict['year'] = None
        day_like = list(filter(lambda x: x.isdigit() and len(x) in (1, 2), date_part))
        if len(day_like) == 1:
            review_date_dict['day'] = int(day_like[0])
        else:
            review_date_dict['day'] = None
        month_like = list(filter(lambda x: not x.isdigit() and len(x) > 2, date_part))
        if len(month_like) == 1:
            review_date_dict['month'] = month_to_int(month_like[0])
        else:
            review_date_dict['month'] = None
        if all(review_date_dict.values()):
            review_date = datetime.datetime(
                review_date_dict['year'],
                review_date_dict['month'],
                review_date_dict['day'],
            )
        else:
            review_date = None
    else:
        review_date = None
        review_country = None
    # Customer name
    customer_name = item_parser.find('span', attrs={'class': 'a-profile-name'})
    customer_name = customer_name.text.strip().replace("\n", " ") if customer_name else ''
    # Title
    review_title = item_parser.find('a', attrs={'data-hook': 'review-title'})
    if review_title:
        review_title = review_title.text.strip().replace("\n", " ").split('.0 out of 5 stars ')
        review_title = review_title[1] if len(review_title) > 1 else ''
    else:
        review_title = ''
    # Content
    review_body = item_parser.find('span', attrs={'data-hook': 'review-body'})
    review_body = review_body.text.strip().replace("\n", " ") if review_body else ''
    # Rating
    review_star_rating = item_parser.find('i', {'data-hook': 'review-star-rating'})
    if not review_star_rating:
        review_star_rating = item_parser.find('i', {'data-hook': 'cmps-review-star-rating'})
    if not review_star_rating:
        review_star_rating = item_parser.find('i', class_='cr-lightbox-review-rating')
    review_rating = float(review_star_rating.find('span').text.split(' ')[0].strip())
    # Helpful votes
    helpful_votes = item_parser.find('span', {'data-hook': 'helpful-vote-statement'})
    if helpful_votes:
        helpful_votes = ''.join(re.findall(r'[0-9]+', helpful_votes.text))
        if helpful_votes:
            helpful_votes = int(helpful_votes)
        else:
            helpful_votes = 1
    else:
        helpful_votes = 0
    # Options
    review_options = (item_parser.find_all('a', {'data-hook': 'format-strip'})
                      or item_parser.find_all('span', {'data-hook': 'format-strip-linkless'}))
    if review_options:
        review_options = review_options[0]
        divider = review_options.find('i')
        if divider:
            review_options = BeautifulSoup(str(review_options).replace(str(divider), ' | '), features='html.parser').text
        else:
            review_options = review_options.text
    else:
        review_options = []
    parse_datetime = datetime.datetime.now(pytz.UTC)

    # data.append({
    #     'Product Link': 'https://www.amazon.com/dp/' + self.params['asin'],
    #     'ASIN': self.params['asin'],
    #     'Review Created Date': review_date,
    #     'Country': review_country,
    #     'Review User Name': customer_name,
    #     'Review Title': review_title,
    #     'Review Body': review_body,
    #     'Review Rating': review_rating,
    #     'Review Helpful Votes': helpful_votes,
    #     'Product Options': review_options,
    # })
    # product_url,asin,date_info,name,title,content,rating,helpful,options
    return {
        'review_id': review_id,
        'product_url': f'https://www.{domain}/dp/{asin}',
        'asin': asin,
        'date': review_date,
        'country': review_country,
        'name': customer_name,
        'title': review_title,
        'description': review_body,
        'rating': review_rating,
        'helpful': helpful_votes,
        'options': review_options,
        'scrap_datetime': parse_datetime,
    }


def parse_aspects(asin, html):
    if isinstance(html, str):
        bs = BeautifulSoup(html, features='html.parser')
    else:
        bs = html
    if not bs:
        print('NO BS! ASIN:', asin)
        return False
    names_div = bs.find(id='aspect-button-group-0')
    root_div = bs.find(attrs={'data-csa-c-slot-id': 'cr-product-insights-cards-popover'})
    if not names_div or not root_div:
        print('NO Aspects! ASIN:', asin)
        return False
    aspects_names = names_div.select('button > span')
    aspects = []
    for aspect in zip(aspects_names, root_div.children):
        quantities = aspect[1].find('div').find_all('span')
        positive = quantities[1].text.replace(',', '').split(' ')
        for i in positive:
            if i.isdigit():
                positive = int(i)
                break
        else:
            return False
        negative = quantities[2].text.replace(',', '').split(' ')
        for i in negative:
            if i.isdigit():
                negative = int(i)
                break
        else:
            return False
        aspects.append((aspect[0].text, positive, negative))
    return aspects


def parse_media_links(html):
    if isinstance(html, str):
        bs = BeautifulSoup(html, features='lxml')
    else:
        bs = html
    try:
        js = bs.find('div', id='imageBlockVariations_feature_div').find('script').text
    except AttributeError as e:
        print(e)
        return None
    data_json = re.search(r"var obj = jQuery.parseJSON\('(.+)'\)", js)
    if not data_json:
        print('no data')
        return None
    data_json_str = data_json.group(1).replace('\n', '').replace('\\', '')
    try:
        data = orjson.loads(data_json_str)
    except:
        print(data_json_str[23490:23530])
        raise
    return data


def get_media_links(asin, data):
    titles_mapping = data['colorToAsin']
    title = None
    for t, value in titles_mapping.items():
        if value['asin'] == asin:
            title = t
            break
    if not title:
        print('no title')
        return [], []
    images_links = []
    for img in data['colorImages'][title]:
        if 'hiRes' in img:
            images_links.append(img['hiRes'])
        else:
            res_max = 0
            media_link = None
            for link, resolution in img['main'].items():
                if int(resolution[0]) > res_max:
                    res_max = int(resolution[0])
                    media_link = link
            if media_link:
                images_links.append(media_link)
    video_links = []
    if data['videos']:
        video_links.append(data['videos'][0]['url'])
    return images_links, video_links


def parse_product(asin, html, tiny=False, domain='amazon.com'):
    if isinstance(html, str):
        bs = BeautifulSoup(html, features='lxml')
    else:
        bs = html
    canonical_link_item = bs.select_one('link[rel="canonical"]')
    if canonical_link_item:
        canonical_link = canonical_link_item['href']
    else:
        canonical_link = None
    if not bs:
        print('NO BS! ASIN:', asin)
        return False
    if Requests.check_captcha(bs):
        print('Kek, captcha :)', asin)
        return -1
    if not bs.select_one('#titleSection, #title, #productTitle'):
        print('NO TITLE! ASIN:', asin)
        return False
    title = bs.select_one('#titleSection, #title, #productTitle').text.strip()
    if tiny == -1:
        brand = bs.select_one('.po-brand')
        if brand:
            brand = brand.text
            if brand:
                brand = brand.replace('Brand', '').strip()
        return title, brand
    descr = bs.select_one('#feature-bullets, #productFactsDesktop_feature_div div[aria-expanded]')
    if not descr:
        print(f'ERROR: ASIN {asin} has no description!')
    else:
        descr = descr.text.strip()
    pic = bs.find(id='landingImage')['src']
    if tiny:
        return title, descr, pic
    features = {}
    top5 = []
    try:
        features_els = bs.select(
            '[data-hook="cr-widget-SummaryAttribute"] #cr-summarization-attributes-list > div'
        )
        for feat in features_els:
            features[feat.find('div > div > div:first-child span').text.strip()] = \
                feat.select_one('div > div > div:last-child > span:last-child').text.strip()
    except:
        pass
    try:
        top5_els = bs.select('[data-hook="lighthut-terms-list"] > div')[:5]
        for lighthum in top5_els:
            top5.append(lighthum.find('span').text.strip())
    except:
        pass
    price = bs.select_one('.a-price')
    if price:
        price = float(price.text.split('$')[1].strip().replace(',', ''))
    else:
        price = None
    return [
        asin, f'https://{domain}/dp/{asin}', canonical_link,
        title, descr, pic, datetime.datetime.now(pytz.UTC),
        features, top5, price,
    ]
