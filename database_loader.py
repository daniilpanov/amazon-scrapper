import database as db
import pandas as pd


filepath = input('Enter the CSV file path: ') or 'aspects_30.11.csv'
collection = input('Enter the name of the collection: ') or 'aspects'
database = input('Enter the name of the database: ') or 'ai_highlights'


df = pd.read_csv(filepath)
res = []
for i, row in df.iterrows():
    res.append(row.to_dict())
db.inst()[database][collection].insert_many(res)
