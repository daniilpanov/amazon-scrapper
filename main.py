
if __name__ == '__main__':
    import math
    import os.path
    import re
    import shutil
    import sys
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event
    from _requests.BaseRequest import STATUS
    from _requests.products_details_collect import products_details_collect
    from _requests.reviews_collect import reviews_collect

    try:
        print('Hey! This is the AmaScrap v3!')
        print('Choose, what do you need? Type the numbers of the operations dividing by colon')
        print('Important note: If you want to gather products\' information/reviews from your list,'
              ' you should create a folder and put a file with the list of ASIN products in text format there.'
              ' The file should be called "products.list".')
        print('1 - gather brands of search requests\n'
              '2 - gather products ASINs (simple gathering)\n'
              '3 - gather products ASINs (gathering by each found brand)\n'
              '4 - gather products details\n'
              '5 - gather products text reviews')
        switches = input('_> ').strip().split(',')
        if not switches:
            print('error')
            sys.exit(0)
        for i in switches:
            if not i.isdigit():
                print('error')
                sys.exit(0)
            item = int(i)
            if item > 5 or item < 1:
                print('error')
                sys.exit(0)

        folder = input('Okay. Now please type the data folder\n_>  ')
        if not os.path.exists(folder) or not os.path.isdir(folder):
            print('This folder does not exist. Creating it')
            os.mkdir(folder)

        print("Okay! Let's start!")

        closed = Event()


        def gather(func, args, statuses, number=None):
            def wrapper():
                global closed
                if closed.is_set():
                    return False
                try:
                    secondary_folder = folder if number is None else folder + str(number)
                    res = func(*args)
                    print('result:', res)
                    lim = 10
                    while res in (STATUS['error'], STATUS['reload']) and lim > 0:
                        res = func(*args)
                        print('result:', res)
                        lim -= 1
                    print('OK!')
                    if res == STATUS['error'] or lim <= 0:
                        print(f'an error occurred in {statuses} gathering to directory {secondary_folder}...')
                    elif res == STATUS['success']:
                        print(f'{statuses} collected to directory ' + secondary_folder)
                    elif res == STATUS['closed']:
                        print('closed')
                        closed.set()
                    else:
                        print(f'unknown status: {statuses} gathering to', secondary_folder + ':', res)
                    if os.path.exists(os.path.join(folder, 'reviews_list.csv')):
                        f = open(os.path.join(folder, 'reviews_list.csv'), 'a')
                        f2 = open(os.path.join(folder, f'reviews_list_{i}.csv'), 'r')
                        lines = f2.readlines()[1:]
                        f2.close()
                        f.writelines(lines)
                        f.close()
                    else:
                        shutil.copyfile(
                            os.path.join(folder, 'reviews_list_{i}.csv'),
                            os.path.join(folder, 'reviews_list.csv'),
                        )
                    os.unlink(os.path.join(folder, f'reviews_list_{i}.csv'))
                    return 'closed' if res == STATUS['closed'] else res == STATUS['success']
                except KeyboardInterrupt:
                    return False

            return wrapper


        # needle questions
        if '1' in switches or '2' in switches or '3' in switches:
            search = input('Please type the search request\n_>  ').strip()
        if '3' in switches or '4' in switches or '5' in switches:
            workers_number = input('Please type the workers number '
                                   '(if you\'ll type not number it will be default value - 4)\n_>  ').strip()
            workers_number = int(workers_number) if workers_number.isdigit() else 4
        # Gathering brands
        if '1' in switches:
            gather('brands', [folder, search], 'brands')()
        # Gathering products (simple)
        if '2' in switches:
            gather('products_simple', [folder, search], 'simple products')()
        # Gathering products (upgraded - by brands)
        if '3' in switches:
            # TODO: see the brands file (if exists) and chunk it between the workers
            gather('products', [folder, search], 'products')()
        # Gathering products details
        if '4' in switches:
            if not os.path.isfile(os.path.join(folder, 'products.list')):
                print('error. list of ASINs not found')
                sys.exit(1)

            f = open(os.path.join(folder, 'products.list'))
            products_list_raw = list(f)
            f.close()
            asins = set()
            pattern = re.compile('[A-Z0-9]{10}')
            for row in products_list_raw:
                if not row.strip():
                    continue
                m = pattern.search(row)
                if m:
                    asins.add(m.group())

            asins = list(asins)

            asins_per_worker = math.ceil(len(asins) / workers_number)

            def multithread_gather(number, asins):
                if not os.path.exists(folder + str(number)):
                    os.mkdir(folder + str(number))
                return gather(products_details_collect, [folder + str(number), asins], 'products\' details', number)

            with ThreadPoolExecutor() as executor:
                features = []
                for i in range(workers_number):
                    asins_iter = asins[i * asins_per_worker:asins_per_worker*(i+1)]
                    features.append(executor.submit(multithread_gather(i, asins_iter)))
                first = True
                for i in range(len(features)):
                    feature = features[i]
                    r = feature.result()
                    if r:
                        if first:
                            shutil.copyfile(
                                os.path.join(folder + str(i), 'products_list.csv'),
                                os.path.join(folder, 'products_list.csv'),
                            )
                            first = False
                        else:
                            f = open(os.path.join(folder, 'products_list.csv'), 'a')
                            f2 = open(os.path.join(folder + str(i), 'products_list.csv'), 'r')
                            lines = f2.readlines()[1:]
                            f2.close()
                            f.writelines(lines)
                            f.close()
                        shutil.rmtree(folder + str(i))

            print('Products list prepared!')
        # Gathering products reviews
        if '5' in switches:
            if not os.path.isfile(os.path.join(folder, 'products.list')):
                print('error. list of ASINs not found')
                sys.exit(1)

            f = open(os.path.join(folder, 'products.list'))
            products_list_raw = list(f)
            f.close()
            asins = set()
            pattern = re.compile('[A-Z0-9]{10}')
            for row in products_list_raw:
                if not row.strip():
                    continue
                m = pattern.search(row)
                if m:
                    asins.add(m.group())

            asins = list(asins)

            executor = ThreadPoolExecutor(max_workers=workers_number)
            features = {}
            for asin in asins:
                features[asin] = executor.submit(gather(reviews_collect, (folder, asin), f'{asin} reviews'))
            executor.shutdown(True)
            print('Reviews list prepared!')
    except KeyboardInterrupt:
        sys.exit(0)
