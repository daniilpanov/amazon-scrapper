import logging
import os
from logging.handlers import TimedRotatingFileHandler

from fastapi import FastAPI
from pydantic import BaseModel

from .crx3packer import package
from .xpi_packer import pack

# Create a logger object
logger = logging.getLogger(__name__)
# Set the logging level to INFO
logger.setLevel(logging.DEBUG)
# Create a handler that logs to the Docker logs
handler = TimedRotatingFileHandler(when='h', backupCount=2, utc=True, filename='logs/server_products_router.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
app = FastAPI()


class ExtensionsListForm(BaseModel):
    ext_list: list


@app.post('/ext/resign/chrome')
def resign_chrome(all_files: bool = False, ext_list: ExtensionsListForm | None = None):
    if not all_files and ext_list:
        extensions_dirs = ext_list.ext_list
    else:
        extensions_dirs = os.listdir('/src/ext')


@app.post('/ext/resign/firefox')
def resign_firefox(all_files: bool = False, ext_list: ExtensionsListForm | None = None):
    if not all_files and ext_list:
        extensions_dirs = ext_list.ext_list
    else:
        extensions_dirs = os.listdir('/src/ext')

