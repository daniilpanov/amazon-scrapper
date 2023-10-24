import pandas as pd
from bs4 import BeautifulSoup
from pandas import DataFrame

fn = input() or 'reviews-list.csv'
data = pd.read_csv(fn)
res = DataFrame(columns=[
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
    item_parser = BeautifulSoup(item['html'], features='html.parser')
    if not item_parser or not item_parser.find(attrs={'data-hook': 'review'}) \
            or item_parser.find('div', class_='a-divider-section') \
            or item_parser.find('h3', attrs={'data-hook': 'dp-global-reviews-header'}):
        continue
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
        review_date = ''
        review_country = ''
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
    review_rating = review_star_rating.find('span').text.split(' ')[0].strip()
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
    review_options = item_parser.find_all('a', {'data-hook': 'format-strip'})
    if review_options:
        review_options = '|'.join(map(lambda x: x.text, review_options)).replace("\n", " ")
    else:
        review_options = ''

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
    res.loc[len(res.index)] = {
        'product_url': 'https://www.amazon.com/dp/' + item['asin'],
        'asin': item['asin'],
        'date_info': review_date_raw,
        'name': customer_name,
        'title': review_title,
        'content': review_body,
        'rating': review_rating,
        'helpful': helpful_votes,
        'options': review_options,
    }

res.to_csv('output_' + fn)
