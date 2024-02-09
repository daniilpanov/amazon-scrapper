import pandas as pd
from json import JSONDecoder

data = []
jsd = JSONDecoder()
first_names = ['Department', 'Category', 'Subcategory']
next_level_categories = 'Subcategory lvl {}'


def rec_get(cat: dict, parent: list[str] | None = None):
    if not cat['is_last_group'] and not cat['items']:
        return
    parents_copied = (parent.copy() + [cat['name']]) if parent else [cat['name']]
    if cat['is_last_group']:
        row_data = {}
        for i in range(min((len(first_names), len(parents_copied)))):
            row_data[first_names[i]] = parents_copied[i]
        if len(parents_copied) > len(first_names):
            for i in range(len(first_names), len(parents_copied)):
                row_data[next_level_categories.format(i)] = parents_copied[i]
        data.append(row_data)
        return
    for child in cat['items']:
        rec_get(child, parents_copied)


with open(input('Введите путь до JSON файла (обычно расположен в папке `tmp__`): ')) as f:
    d = jsd.decode(f.read())

for item in d['items']:
    rec_get(item)

df = pd.DataFrame(data)
df.to_csv(input('Введите имя выходного файла [departments_output.csv]') or 'departments_output.csv', index=False)
