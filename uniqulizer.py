# -*- coding: utf-8 -*-


def uniqulize(filepath, output='output.csv'):
    with open(filepath, encoding='utf-8') as f:
        datalist = [row.strip() + '\n' for row in f]
        dataset = set(datalist)

    with open(output, 'w', encoding='utf-8') as f:
        for row in datalist:
            if row in dataset:
                dataset.remove(row)
                f.write(row)


if __name__ == '__main__':
    # uniqulizer
    import os.path

    path: str = "reviews.csv"
    while not os.path.exists(os.path.abspath(path)):
        path = input("Please, input the filepath: ")

    uniqulize(path)
