import pandas as pd

import tasks_manager

df = pd.read_csv('ai_highlights.departments.csv', index_col=None)
tasks = []
df = df.reset_index()
for index, row in df.iterrows():
    print(row['URL'])
    if not row['URL'] or row['URL'] == 'nan' or not isinstance(row['URL'], str):
        continue
    tasks.append({'bsr': row['URL']})
print('OK')
tasks_manager.add_task('bsrmarket', {}, tasks)
