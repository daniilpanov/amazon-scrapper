if __name__ == '__main__':
    # uniquliser
    import os.path

    filepath: str = "reviews.csv"
    while not os.path.exists(os.path.abspath(filepath)):
        filepath = input("Введите путь до файла: ")

    with open(filepath) as f:
        data = set(row.strip() + '\n' for row in f)

    with open('output.csv', 'w') as f:
        f.writelines(data)
