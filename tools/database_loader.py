import csv
import datetime
import os
import argparse
from pymongo import MongoClient
from pymongo.errors import PyMongoError

class CSVImporter:
    def __init__(self, mongo_uri, db_name, collection_name, csv_path, state_file='import_state.txt', chunk_size=1000):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.collection_name = collection_name
        self.csv_path = csv_path
        self.state_file = state_file
        self.chunk_size = chunk_size
        self.processed_rows = 0
        self.file_position = 0
        self.headers = []

    def _load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                self.file_position = int(f.read().strip())
        return self.file_position

    def _save_state(self):
        with open(self.state_file, 'w') as f:
            f.write(str(self.file_position))

    def _process_row(self, row):
        processed = dict(row)
        del processed['_id']
        if processed['date']:
            dt = processed['date'] = datetime.datetime.fromisoformat(processed['date'])
            processed['date_key'] = datetime.datetime.combine(dt.date(), datetime.time())
        return processed

    def import_data(self):
        try:
            # Загрузка последнего состояния
            start_position = self._load_state()

            with open(self.csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                # Пропускаем уже обработанные байты
                csvfile.seek(start_position)

                reader = csv.DictReader(csvfile)
                self.headers = reader.fieldnames

                chunk = []
                current_position = start_position

                for row in reader:
                    current_position = csvfile.tell()
                    processed_row = self._process_row(row)
                    chunk.append(processed_row)
                    self.processed_rows += 1

                    if len(chunk) >= self.chunk_size:
                        self.collection.insert_many(chunk)
                        self.file_position = current_position
                        self._save_state()
                        print(f"Processed {self.processed_rows} rows")
                        chunk = []

                # Вставка оставшихся документов
                if chunk:
                    self.collection.insert_many(chunk)
                    self.file_position = current_position
                    self._save_state()

            print(f"Import completed. Total rows processed: {self.processed_rows}")
            # Очистка файла состояния после завершения
            os.remove(self.state_file)

        except (PyMongoError, IOError, csv.Error) as e:
            print(f"Error occurred: {str(e)}")
            print(f"Last successful position: {self.file_position}")
            self._save_state()
        finally:
            self.client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='CSV to MongoDB Importer')
    parser.add_argument('--mongo_uri', required=True, help='MongoDB connection URI')
    parser.add_argument('--db', required=True, help='Database name')
    parser.add_argument('--collection', required=True, help='Collection name')
    parser.add_argument('--csv', required=True, help='Path to CSV file')
    parser.add_argument('--state', default='import_state.txt', help='State file path')
    parser.add_argument('--chunk', type=int, default=1000, help='Chunk size')

    args = parser.parse_args()

    importer = CSVImporter(
        mongo_uri=args.mongo_uri,
        db_name=args.db,
        collection_name=args.collection,
        csv_path=args.csv,
        state_file=args.state,
        chunk_size=args.chunk
    )

    importer.import_data()

# python script.py \
#   --mongo_uri "mongodb://localhost:27017" \
#   --db mydatabase \
#   --collection mycollection \
#   --csv data.csv \
#   --state import.state \
#   --chunk 5000
