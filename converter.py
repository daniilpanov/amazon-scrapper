import os


def convert(f_input, f_output='output_reviews_list_converted.csv'):
    if not os.path.exists(f_input):
        return False
    
    exists = os.path.exists(f_output)
    
    months = ['January', 'February', 'March', 'April', 'May',
              'June', 'July', 'August', 'September', 'October', 'November', 'December']
    
    with open(f_input, encoding='utf-8') as f, open(f_output, 'a' if exists else 'w', encoding='utf-8') as of:
        # header
        try:
            next(f)
            if not exists:
                of.write('product_url,asin,date,country,name,title,content,rating,helpful,options\n')
            while True:
                # line preparing
                line = next(f)
                line_parsed = line.split(',', maxsplit=4)
                date_info = line_parsed[2][17:] if line_parsed[2][13] == 't' else line_parsed[2][13:]
                country, date_info = date_info.split(' on ', maxsplit=1)
                # parse date
                m, d = date_info.split(' ')
                m = months.index(m) + 1
                y = line_parsed[3][1:5]
                date = f'{y}-{m:02}-{int(d):02}'
                # country and date prepared
                line = ','.join(line_parsed[:2] + [date, country] + [line_parsed[4]])
                of.write(line)
        except StopIteration:
            print('Success')
            return True


if __name__ == '__main__':
    # for i in ['ABSA - Pressure-cookers', 'ABSA - recovery-drink', 'ABSA - Rice-cookers', 'ABSA - wine-coolers']:
    #     print(convert('WRPR/' + i + '.csv', 'WRPR/' + i + '_converted.csv'))
    #     print(convert('WRPR/' + i + '.csv', 'WRPR/all_converted.csv'))
    print(convert('reviews_list_old.csv', 'reviews_list.csv'))
