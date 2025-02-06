import db_mongo as db
import pandas as pd

df = pd.read_csv('test2.csv', index_col=0)
needle = ['B072Z7M7JZ', 'B0819FZ3N7', 'B0948TSRGS', 'B07YNXG2HZ', 'B076FG7V61', 'B09LGTWHKF']
df = df.query("asin in ('" + "','".join(needle) + "')")
vals = list(df.T.to_dict().values())
print(vals[0])
db.db('ai_highlights')['aspects'].insert_many(vals, False)
