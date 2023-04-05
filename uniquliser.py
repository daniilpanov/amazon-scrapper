# -*- coding: utf-8 -*- 

if __name__ == '__main__':
    # uniquliser
    import os.path

    filepath: str = "reviews.csv"
    while not os.path.exists(os.path.abspath(filepath)):
        filepath = input("Please, input the filepath: ")

    with open(filepath, encoding='utf-8') as f:
        datalist = [row.strip() + '\n' for row in f]
        dataset = set(datalist)

    with open('output.csv', 'w', encoding='utf-8') as f:
        for row in datalist:
            if row in dataset:
                dataset.remove(row)
                f.write(row)
