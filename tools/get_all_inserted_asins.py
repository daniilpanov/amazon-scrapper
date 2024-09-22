from db_mongo import db


def get_data(alias):
    print('---', alias, '---')
    groups = db('scrap_process')['tasks_groups'].find({'script': 'products'})
    asins = set()
    for group in groups:
        if alias in group['alias']:
            for body in group.get('taskBodies', []):
                asins.add(body['data']['asin'])

    asins = list(asins)
    print('Count asins:', len(asins))
    print('Asins list:', asins)

    # product_card
    prod_cards = list(db('amazon_data')['product_card'].find({'asin': {'$in': asins}}))
    print('Count product cards: ', len(prod_cards))
    print('Without features:', end=' ')
    for card in prod_cards:
        if not card.get('features'):
            print(card['asin'] + ',', end=' ')
    print()
    print('Without top_5_phrases:', end=' ')
    for card in prod_cards:
        if not card.get('top_5_phrases'):
            print(card['asin'] + ',', end=' ')
    print()

    # customer_reviews
    for asin in asins:
        print('Reviews for asin', asin + ':', db('amazon_data')['customer_reviews'].count_documents({'asin': asin}))

    # aspects
    for asin in asins:
        print('Aspects for asin', asin + ':', db('amazon_data')['aspects'].count_documents({'ASIN': asin}))


if __name__ == '__main__':
    # get_data('Lakanto-2#reviews')
    # get_data('Ingarden#reviews')
    # get_data('Lakanto#reviews')
    get_data('ingarden#reviews')
