from io import BytesIO
from typing import BinaryIO

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

import settings

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = settings.SERVICE_ACCOUNT_FILE

try:
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
except FileNotFoundError:
    credentials = service_account.Credentials.from_service_account_file(
        '../' + SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=credentials)


def get_files(fields: str | None = None, q: str | None = None):
    if fields is None:
        fields = 'id, name, mimeType, parents, createdTime, permissions, quotaBytesUsed'
    results = service.files().list(pageSize=10, q=q,
                                   fields=f'nextPageToken, files({fields})').execute()
    next_page_token = results.get('nextPageToken')
    while next_page_token:
        next_page = service.files().list(
            pageSize=10,
            fields=f'nextPageToken, files({fields})',
            pageToken=next_page_token,
            q=q,
        ).execute()
        next_page_token = next_page.get('nextPageToken')
        results['files'] = results['files'] + next_page['files']
    return results.get('files')


def get_files_about_asin(asin):
    results = service.files().list(pageSize=10, q=f'name contains \'{asin}\'',
                                   fields='nextPageToken, files(id, name)').execute()
    next_page_token = results.get('nextPageToken')
    while next_page_token:
        next_page = service.files().list(
            pageSize=10,
            fields=f'nextPageToken, files(id, name)',
            pageToken=next_page_token,
            q=f'name contains \'{asin}\'',
        ).execute()
        next_page_token = next_page.get('nextPageToken')
        results['files'] = results['files'] + next_page['files']
    return results.get('files')


def delete_duplicate_files():
    try:
        results = service.files().list(fields="nextPageToken, files(id, name, createdTime)").execute()
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
                    service.files().delete(fileId=file['id']).execute()
    except HttpError as error:
        print(f'Произошла ошибка: {error}')


def load_file(io: BinaryIO | BytesIO, filename: str, mimetype: str):
    return service.files().create(body={
        'name': filename,
    }, media_body=MediaIoBaseUpload(io, mimetype, resumable=True)).execute()


def download_file(file_id):
    try:
        # pylint: disable=maybe-no-member
        request = service.files().get_media(fileId=file_id)
        file_content = BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)
        done = False
        while done is False:
            stat, done = downloader.next_chunk()
    except HttpError as error:
        print(f"An error occurred: {error}")
        file_content = None
    return file_content.getvalue()
