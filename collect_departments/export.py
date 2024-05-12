import os
import csv
import typing

from db import Department


def get_data():
    data = list(Department.select())

    data_dict = {}
    data_parent_dict = {}

    for item in data:
        _id = int(str(item.id))
        parent_id = int(str(item.parent_id)) if item.parent_id > 0 else None
        data_dict[_id] = item
        if parent_id not in data_parent_dict:
            data_parent_dict[parent_id] = [item]
        else:
            data_parent_dict[parent_id].append(item)
        if parent_id in data_dict:
            data_dict[parent_id].items = data_parent_dict[parent_id]
        if _id in data_parent_dict:
            item.items = data_parent_dict[_id]
    return data_dict


def rec(department, parent_chain=None):
    if not parent_chain:
        parent_chain = []
    parent_chain = parent_chain.copy()
    if not department.items:
        parent_chain.append(department)
        return [parent_chain]
    parent_chain.append(department)
    rows = []
    for it in department.items:
        rows.extend(rec(it, parent_chain))
    return rows


def export(filename: str, *, delimiter=',', quotechar='"', lim=None, _in=None):
    data_dict = get_data()

    q = (Department.parent_id == 0)
    if isinstance(lim, typing.Sized):
        if len(lim) > 0:
            q &= (Department.id <= lim[0])
        if len(lim) > 1:
            q &= (Department.id >= lim[1])
    if isinstance(_in, typing.Iterable):
        q &= (Department.id in _in)

    first_departments = list(Department.select().where(q))

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=delimiter,
                            quotechar=quotechar, quoting=csv.QUOTE_MINIMAL)
        for fd in first_departments:
            r = rec(data_dict[int(str(fd))])
            for rr in r:
                nr = []
                for i in rr:
                    nr.append(i.name)
                nr.append(i.url)
                writer.writerow(nr)


if __name__ == '__main__':
    export('result.csv')
