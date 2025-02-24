import json

with open('resultKWT.json', encoding='UTF-8') as f:
    data = json.loads(f.read())

new_data = []


def setdefaultmany(obj, keys, func, default = None):
    for k in keys:
        obj[k] = func(obj[k]) if obj.get(k) else default


organic_count = 0
sponsored_count = 0

for item in filter(lambda i: i, data):
    setdefaultmany(item, ('score', 'price', 'itemPrice', 'oldPrice', 'subscriptionDiscount', 'subscriptionDiscountPercents'), float)
    setdefaultmany(item, ('BestSellerIn', 'image', 'title', 'asin'), str, None)
    item['sponsored_rank'] = None
    item['organic_rank'] = None
    if item.get('isSponsored'):
        sponsored_count += 1
        item['sponsored_rank'] = sponsored_count
    else:
        organic_count += 1
        item['organic_rank'] = organic_count
    del item['isSponsored']
    # print(item)
    new_data.append(item)

with open('reskwt.json', 'w', encoding='UTF-8') as f:
    f.write(json.dumps(new_data))

