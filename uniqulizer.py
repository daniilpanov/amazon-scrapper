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


def uniqulize_by_df(filepath, output='output.csv', header_row=None):
    import pandas
    df = pandas.read_csv(filepath, header=header_row)
    df.drop_duplicates().to_csv(output, index=False, header=(header_row == 0))


if __name__ == '__main__':
    # uniqulizer
    import os.path

    path = "reviews.csv"
    f_out = "output.csv"
    header = False
    while not os.path.exists(os.path.abspath(path)):
        path = input("Please, type the filepath: ")
        header = input("Have this file header? [yes/no]: ").lower() in ('yes', 'y')
        f_out = input("Please, type the output file or just press enter to choose default filepath - ./output.csv: ") \
                or "output.csv"

    uniqulize_by_df(path, f_out, 0 if header else None)
