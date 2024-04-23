from io import BytesIO
from typing import BinaryIO

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

import amazon_requests
import collect_products

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'amascrap3-421123-bf6920748193.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=credentials)


def get_files(fields: str | None = None, q: str | None = None):
    if fields is None:
        fields = 'id, name, mimeType, parents, createdTime, permissions, quotaBytesUsed'
    results = service.files().list(pageSize=10,
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


async def main():
    sess = amazon_requests.Requests()
    await sess.init()
    await collect_products.get_item(None, 'B019ZZB3O2', sess, None, set(), False, True)
    await sess.request.close()

