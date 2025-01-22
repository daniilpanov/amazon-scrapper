import json
import logging
import os
import hashlib
import xml.etree.ElementTree as ET
from contextlib import asynccontextmanager
from json import JSONDecoder
from logging.handlers import TimedRotatingFileHandler
from os.path import isdir

from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from requests import JSONDecodeError

from .crx3packer import package as crx3pack
from .xpi_packer import pack as xpipack

server_host = ('https://' if os.environ.get('HTTPS_READY') == 'true' else 'http://') + os.environ.get('HOST',
                                                                                                      'localhost')
this_port = os.environ.get('EXT_PACKER_PORT', 8091)

# Создаем объект логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = TimedRotatingFileHandler(when='h', backupCount=2, utc=True, filename='logs/ext_packer.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


@asynccontextmanager
async def lifespan(_: FastAPI):
    extensions_dirs = os.listdir('ext')
    # cmds_map = [lambda folder, _: logger.error('Ошибка при упаковке', folder), crx3pack, xpipack]
    cmds_map = [crx3pack, crx3pack, xpipack]
    for folder in extensions_dirs:
        path = os.path.join('ext', folder)
        if not isdir(path):
            continue
        try:
            cmds_map[folder.endswith('chrome') + folder.endswith('firefox') * 2](path, 'compiled_ext/')
        except Exception as e:
            logger.error(f'Ошибка при обработке {folder}: {e}')
    generate_update_xml()  # Генерируем update.xml после успешного подписания
    yield


app = FastAPI(lifespan=lifespan)
router = APIRouter(prefix='/ext')


class ExtensionsListForm(BaseModel):
    ext_list: list


def sign(dirs_list, func):
    success = []
    failures = []
    for folder in dirs_list:
        try:
            func(folder, 'compiled_ext/')
            success.append(folder)
        except Exception as e:
            logger.error(f'Ошибка при подписывании {folder}: {e}')
            failures.append(folder)
    return success, failures


@router.post('/resign/chrome')
def resign_chrome(all_files: bool = False, ext_list: ExtensionsListForm | None = None):
    if not all_files and ext_list:
        extensions_dirs = ext_list.ext_list
    else:
        all_dirs = os.listdir('ext')
        extensions_dirs = []

        for ext in all_dirs:
            path = os.path.join('ext', ext)
            # if isdir(path) and ext.endswith('chrome'):
            if isdir(path):
                extensions_dirs.append(path)

    success, failures = sign(extensions_dirs, crx3pack)

    if failures:
        raise HTTPException(status_code=400, detail={"success": success, "failures": failures})

    generate_update_xml()  # Генерируем update.xml после успешного подписания
    return {"success": success}


@router.post('/resign/firefox')
def resign_firefox(all_files: bool = False, ext_list: ExtensionsListForm | None = None):
    if not all_files and ext_list:
        extensions_dirs = ext_list.ext_list
    else:
        all_dirs = os.listdir('ext')
        extensions_dirs = []

        for ext in all_dirs:
            path = os.path.join('ext', ext)
            if isdir(path) and ext.endswith('firefox'):
                extensions_dirs.append(path)

    success, failures = sign(extensions_dirs, xpipack)

    if failures:
        raise HTTPException(status_code=400, detail={"success": success, "failures": failures})

    generate_update_xml()  # Генерируем update.xml после успешного подписания
    return {"success": success}


def generate_extension_id(manifest_path):
    """Генерирует ID расширения на основе содержимого manifest.json."""
    with open(manifest_path, 'rb') as f:
        manifest_content = f.read()
    return hashlib.sha256(manifest_content).hexdigest()[:32]  # Первые 32 символа хеша


def generate_update_xml():
    update_metadata_path = 'update_metadata/'
    os.makedirs(update_metadata_path, exist_ok=True)

    # Сбор информации о расширениях
    for folder in os.listdir('compiled_ext/'):
        if folder.endswith('.crx'):
            ext_name = folder[:-4]
            manifest_path = os.path.join('ext', ext_name, 'manifest.json')
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, 'r', encoding='utf-8') as mf:
                        version = json.loads(mf.read()).get('version', '1.0')
                except JSONDecodeError:
                    version = '1.0'
                app_id = generate_extension_id(manifest_path)  # Генерируем ID расширения
                codebase = f"{server_host}:{this_port}/ext/get/{folder}"

                # Создание XML для каждого расширения
                root = ET.Element("gupdate", xmlns="http://www.google.com/update2/response", protocol="2.0")
                app_element = ET.SubElement(root, "app", appid=app_id)
                updatecheck = ET.SubElement(app_element, "updatecheck", codebase=codebase, version=version)

                # Сохранение XML в файл
                update_file_path = os.path.join(update_metadata_path, f"{ext_name}.xml")
                tree = ET.ElementTree(root)
                tree.write(update_file_path, encoding='utf-8', xml_declaration=True)


@router.get('/update/{ext_name}.xml', response_class=FileResponse)
def get_update_xml(ext_name: str):
    update_file_path = os.path.join('update_metadata/', f"{ext_name}.xml")
    if os.path.exists(update_file_path):
        return FileResponse(update_file_path)
    else:
        raise HTTPException(status_code=404, detail="Update file not found")


@router.get('/get/{ext_name}.crx', response_class=FileResponse)
def get_update_xml(ext_name: str):
    update_file_path = os.path.join('compiled_ext/', f"{ext_name}.crx")
    if os.path.exists(update_file_path):
        return FileResponse(update_file_path)
    else:
        raise HTTPException(status_code=404, detail="Update file not found")


app.include_router(router)
