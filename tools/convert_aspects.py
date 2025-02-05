import pandas as pd

df = pd.read_csv('asp30_11 .csv')

print(df)

del df['country']
del df['date']
del df['name']
del df['title']
del df['content']
del df['description']
del df['rating']
del df['helpful']
del df['options']
print(df)

df.to_csv('aspects_30.11.csv', index=False)
