import database as db

reviews_ready = [el['review_id'] for el in db.db()['temp_customer_reviews'].find({})]
data = db.db()['customer_reviews'].find({'review_id': {'$nin': list(reviews_ready)}})
new_data = {}

for item in data:
    new_data[item['review_id']] = item
db.db()['temp_customer_reviews'].insert_many(new_data.values())
# asin = None
# for item in data:
#     if item['asin'] != asin:
#         asin = item['asin']
#         print(asin)
#     try:
#         db.db()['temp_customer_reviews'].insert_one(item)
#     except:
#         pass

