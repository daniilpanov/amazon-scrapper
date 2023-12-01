import database as db

collection = input('Please enter the collection name: ') or 'customer_reviews'
temp_collection = input('Please enter the temp collection name: ') or 'temp_' + collection
uniq_col = input('Enter the unique column: ') or 'review_id'

els_ready = [el[uniq_col] for el in db.db()[temp_collection].find({})]
data = db.db()[collection].find({uniq_col: {'$nin': list(els_ready)}} if els_ready else {})
new_data = {}

for item in data:
    new_data[item[uniq_col]] = item
try:
    db.db()[temp_collection].insert_many(new_data.values())
except:
    pass
asin = None
for item in data:
    if item.get('asin') != asin:
        asin = item['asin']
        print(asin)
    try:
        db.db()[temp_collection].insert_one(item)
    except:
        pass

