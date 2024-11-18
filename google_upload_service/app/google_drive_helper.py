from typing import BinaryIO

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload

import config

SCOPES = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
DEFAULT_SERVICE_FILE = config.DEFAULT_SERVICE_FILE


def build_service(file_suffix: str = None):
    filename = 'amazon-' + (file_suffix or DEFAULT_SERVICE_FILE) + '.json'
    try:
        credentials = service_account.Credentials.from_service_account_file(filename, scopes=SCOPES)
    except FileNotFoundError:
        credentials = service_account.Credentials.from_service_account_file('../' + filename, scopes=SCOPES)
    return build('drive', 'v3', credentials=credentials)


services = {
    'target': build_service('target'),
    'sellercentral': build_service('sellercentral'),
}
if DEFAULT_SERVICE_FILE:
    services[None] = services[DEFAULT_SERVICE_FILE]


def delete_duplicate_files(serv=None):
    try:
        results = services[serv].files().list(fields="nextPageToken, files(id, name, createdTime)").execute()
        all_files = results.get('files', [])

        # Группируем файлы по имени
        files_by_name = {}
        for file in all_files:
            if file['name'] in files_by_name:
                files_by_name[file['name']].append(file)
            else:
                files_by_name[file['name']] = [file]

        # Для каждого имени файла, где есть более одной копии, удаляем дубликаты
        for file_name, files in files_by_name.items():
            if len(files) > 1:
                # Сортируем файлы по дате создания, самый новый файл будет первым
                sorted_files = sorted(files, key=lambda x: x['createdTime'], reverse=True)
                # Оставляем самый новый файл, удаляем остальные
                for file in sorted_files[1:]:
                    services[serv].files().delete(fileId=file['id']).execute()
    except HttpError as error:
        print(f'Произошла ошибка: {error}')


def load_file(io: BinaryIO, filename: str, mimetype: str, serv=None):
    return services[serv].files().create(body={
        'name': filename,
    }, media_body=MediaIoBaseUpload(io, mimetype, resumable=True)).execute()

