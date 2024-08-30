import datetime
import os.path
from numpy import NAN

import orjson

if os.path.exists('tmpres.json'):
    with open('tmpres.json', encoding='utf-8') as f:
        data = orjson.loads(f.read())
else:
    from db_mongo import db

    data = db('Ads')['test'].find()
    data = data.next()

    with open('tmpres.json', mode='wb') as f:
        f.write(str(data).replace("'_id': ObjectId('66d0dc898592bd7424602f00'), ", '').replace("'", '"').replace('None', 'null').replace('True', 'true').replace('False', 'false').encode('utf-8'))

raw_specs = data['reportSpecification']
m_ids = ','.join(raw_specs['marketplaceIds'])
new_data = []

for item in data['dataByAsin']:
    new_item = {
        'start_date': raw_specs['dataStartTime'],
        'end_date': raw_specs['dataEndTime'],
        'asin': item['asin'],
        'orders': item['orders'],
        'unique_customers': item['uniqueCustomers'],
        'repeat_customers_pct_total': item['repeatCustomersPctTotal'],
        'repeat_purchase_revenue_pct_total': item['repeatPurchaseRevenuePctTotal'],
        'repeat_purchase_revenue_amount': item['repeatPurchaseRevenue']['amount'],
        'repeat_purchase_revenue_currency_code': item['repeatPurchaseRevenue']['currencyCode'],
        'repeat_purchase_revenue': NAN,
        'seller_id': None,  # TODO: ???
        'date_start': datetime.datetime.fromisoformat(item['startDate']),
        'date_end': datetime.datetime.fromisoformat(item['endDate']),
        'period': raw_specs['reportOptions']['reportPeriod'],
        'marketplace_ids': m_ids,
    }
    new_data.append(new_item)
    print(new_item)
    break
