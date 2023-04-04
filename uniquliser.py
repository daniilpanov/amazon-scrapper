if __name__ == '__main__':
    # uniquliser
    import os.path

    filepath: str = "reviews.csv"
    while not os.path.exists(os.path.abspath(filepath)):
        filepath = input("Введите путь до файла: ")

    with open(filepath, encoding='utf-8') as f:
        data = set(row.strip() + '\n' for row in f if
                   row.strip() != 'product_url,asin,date_info,name,title,content,rating,helpful,options')

    with open('output.csv', 'w', encoding='utf-8') as f:
        f.write('product_url,asin,date_info,name,title,content,rating,helpful,options' + '\n')
        f.writelines(data)
