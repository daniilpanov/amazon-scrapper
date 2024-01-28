import pandas as pd
import database as db

if __name__ == '__main__':
    if input('Are you sure?').lower() == 'yes':
        collection = input('Enter the collection name [amazon_data.customer_reviews]: ') or 'amazon_data.customer_reviews'
        uniq_cols = (input('Enter the unique columns, divided by ",": ') or 'review_id').split(',')
        db_name, collection = collection.split('.')
        try:
            c = db.db(db_name)[collection]
            data = list(c.find({}))
        except:
            c = db.spec_db(db_name)[collection]
            data = list(c.find({}))
        df = pd.DataFrame(data)
        print('Data saved to local DataFrame')
        df = df.drop_duplicates(subset=uniq_cols)
        print('Duplicates dropped')
        c.delete_many({})
        print('Deleted old data')
        c.insert_many(df.T.to_dict().values())
        print('Inserted uniqulized data')
