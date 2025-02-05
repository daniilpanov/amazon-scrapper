from db_mongo import db
import tasks_manager

data = db('ai_highlights')['departments'].find({'URL': {'$exists': True}, 'items': {'$exists': False}})
tasks = []
for row in data:
    if not row.get('URL') or row['URL'].lower() == 'nan' or not isinstance(row['URL'], str):
        continue
    print(row['URL'])
    tasks.append({'bsr': row['URL']})
print('OK')
tasks_manager.add_task('bsrmarket', {}, tasks)
