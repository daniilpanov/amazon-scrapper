
if __name__ == '__main__':
    import math
    import os.path
    import re
    import shutil
    import sys
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event
    from _requests.BaseRequest import STATUS

    try:
        print('Hey! This is AmaScrap v3!')
        print('Choose what you need? Enter transaction numbers, separating them with a comma')
        print('Important Note: If you want to collect information/reviews about products from your list,'
              ' you should create a folder and place the ASIN product list file in text format there.'
              ' The file should be called "products.list".')
        print('1 - collect products ASINs\n'
              '2 - collect products details\n'
              '3 - collect products text reviews')
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

        folder = input('Fine. Now enter the data folder name\n_>  ')
        if not os.path.exists(folder) or not os.path.isdir(folder):
            print('This folder does not exist. Create it')
            os.mkdir(folder)

        print("Okay! Let's start!")

        closed = Event()


        def gather(func, args, statuses, filename=None, base_filename=None, number=None):
            def wrapper():
                global closed
                if closed.is_set():
                    return False
                try:
                    secondary_folder = folder if number is None else folder + str(number)
                    res = func(*args)
                    lim = 10
                    while res in (STATUS['error'], STATUS['reload']) and lim > 0:
                        res = func(*args)
                        lim -= 1
                    if res == STATUS['error'] or lim <= 0:
                        print(f'an error occurred in {statuses} collecting to directory {secondary_folder}...')
                    elif res == STATUS['success']:
                        print(f'{statuses} collected to directory ' + secondary_folder)
                    elif res == STATUS['closed']:
                        print('closed')
                        closed.set()
                    else:
                        print(f'unknown status: {statuses} collecting to', secondary_folder + ':', res)

                    if filename and base_filename:
                        if os.path.exists(base_filename):
                            f = open(base_filename, 'a')
                            f2 = open(filename, 'r')
                            lines = f2.readlines()[1:]
                            f2.close()
                            f.writelines(lines)
                            f.close()
                        else:
                            shutil.copyfile(filename, base_filename)
                        os.unlink(filename)
                    return 'closed' if res == STATUS['closed'] else res == STATUS['success']
                except KeyboardInterrupt:
                    return False

            return wrapper


        # needle questions
        if '2' in switches or '3' in switches:
            workers_number = input('Enter the maximum number of parallel jobs '
                                   '(if you enter not a number, the default value will be 4)\n_>  ').strip()
            workers_number = int(workers_number) if workers_number.isdigit() else 4
        # Gathering products
        if '1' in switches:
            from _requests.products_collect import products_collect
            search = input('Enter the search request\n_>  ').strip()
            gather(products_collect, [folder, search], 'simple products')()
        # Gathering products details
        if '2' in switches:
            from _requests.products_details_collect import products_details_collect
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
                return gather(
                    products_details_collect,
                    [folder + str(number), asins],
                    'products\' details',
                    os.path.join(folder + str(number), 'products_list.csv'),
                    os.path.join(folder, 'products_list.csv'),
                    number)

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
                        shutil.rmtree(folder + str(i))

            print('Products list prepared!')
        # Gathering products reviews
        if '3' in switches:
            from _requests.reviews_collect import reviews_collect

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
                features[asin] = executor.submit(
                    gather(
                        reviews_collect,
                        (folder, asin),
                        f'{asin} reviews',
                        os.path.join(folder, f'reviews_list_{asin}.csv'),
                        os.path.join(folder, 'reviews_list.csv'),
                    )
                )
            executor.shutdown(True)
            print('Reviews list prepared!')
    except KeyboardInterrupt:
        sys.exit(0)
