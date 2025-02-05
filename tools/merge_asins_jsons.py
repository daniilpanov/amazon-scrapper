import json
import os

asins = set()
data = []

for item in os.listdir('.'):
    if not item.startswith('amz') or not item.endswith('.json'):
        continue
    with open(item, 'r', encoding='utf-8') as f:
        data_item = json.loads(f.read())
    for datum in data_item:
        old_s = len(asins)
        asins.add(datum.get('asin', ''))
        if old_s < len(asins):
            data.append(datum)

print(len(data))
with open('amzscout-res-all.json', 'w', encoding='utf-8') as rf:
    rf.write(json.dumps(data))
