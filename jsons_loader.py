
import pandas as pd
import pymongo.errors

from db_mongo import db


def load_json_to_mongodb(collection_name, chunk_size=10000):
    c1 = db('amazon_reports')[collection_name]
    c2 = db('amazon_reports_dev')[collection_name]

    for json_file in ['amazon_reports.' + collection_name + '.json', 'amazon_reports_dev.' + collection_name + '.json']:
        # Читаем JSON файл в DataFrame
        try:
            df = pd.read_json(json_file)
            df = df.drop('_id', axis=1)
            # Преобразуем DataFrame в список словарей
            data = df.to_dict(orient='records')
            # Вставляем данные в коллекцию MongoDB в чанках
            if data:
                for i in range(0, len(data), chunk_size):
                    chunk = data[i:i + chunk_size]  # Получаем чанк данных
                    try:
                        c1.insert_many(chunk, ordered=False)
                    except pymongo.errors.BulkWriteError as e:
                        ...  # print(f'Ошибка вставки в коллекцию {collection_name} (amazon_reports): {e}')
                    try:
                        c2.insert_many(chunk, ordered=False)
                    except pymongo.errors.BulkWriteError as e:
                        ...  # print(f'Ошибка вставки в коллекцию {collection_name} (amazon_reports_dev): {e}')
                print(f'Загружено {len(data)} записей из {json_file} в коллекцию {collection_name}.')
            else:
                print(f'Файл {json_file} пуст, ничего не загружено.')
        except ValueError as e:
            print(f'Ошибка при чтении {json_file}: {e}')
        except Exception as e:
            print(f'Произошла ошибка при загрузке данных из {json_file}: {e}')
            raise e


# Пример использования:
load_json_to_mongodb('market_basket')
