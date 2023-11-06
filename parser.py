import datetime

import pandas as pd
import pytz
from bs4 import BeautifulSoup
from pandas import DataFrame


def parse_reviews(asin, html):
    item_parser = BeautifulSoup(html, features='html.parser')
    if not item_parser or not item_parser.find(attrs={'data-hook': 'review'}) \
            or item_parser.find('div', class_='a-divider-section') \
            or item_parser.find('h3', attrs={'data-hook': 'dp-global-reviews-header'}):
        return False
    review_id = item_parser.find('div', attrs={'data-hook': 'review'})['id']
    # Country & Date
    review_date_raw = item_parser.find('span', attrs={'data-hook': 'review-date'})
    if review_date_raw:
        review_date_raw = review_date_raw.text.strip()
        review_date = review_date_raw.replace("\n", " ") \
            .replace('Reviewed in the ', '').replace(',', '').replace('"', '')
        rdc = review_date.split(' on ')
        review_date = rdc[-1]
        review_country = ' on '.join(rdc[:-1])
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
        helpful_votes = helpful_votes.text.split(' ')[0]
        if helpful_votes == 'One':
            helpful_votes = 1
        else:
            helpful_votes = int(helpful_votes.replace(',', ''))
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
        'product_url': 'https://www.amazon.com/dp/' + asin,
        'asin': asin,
        'date': review_date,
        'country': review_country,
        'name': customer_name,
        'title': review_title,
        'content': review_body,
        'rating': review_rating,
        'helpful': helpful_votes,
        'options': review_options,
        'scrap_datetime': parse_datetime,
    }


if __name__ == '__main__':
    fn = input() or 'reviews-list.csv'
    data = pd.read_csv(fn)
    res = DataFrame(columns=[
        'review_id',
        'product_url',
        'asin',
        'date_info',
        'name',
        'title',
        'content',
        'rating',
        'helpful',
        'options',
    ])

    for index, item in data.iterrows():
        d = parse(item['asin'], item['html'])
        if d:
            res.loc[len(res.index)] = d

    res.to_csv('output_' + fn)


def parse_product(asin, html):
    bs = BeautifulSoup(html, features='html.parser')
    title = bs.select_one('#titleSection, #title, #productTitle').text.strip()
    descr = bs.find(id='feature-bullets').text.strip()
    pic = bs.find(id='landingImage')['src']
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
        price = float(price.text.split('$')[1].strip())
    else:
        price = None
    return [
        asin, f'https://amazon.com/dp/{asin}',
        title, descr, pic, datetime.datetime.now(pytz.UTC),
        features, top5, price,
    ]
