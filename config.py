import os
import dotenv


def update_config():
    with open('.env', 'w') as env_file:
        env_file.writelines([
            f'WEBDRIVER_PATH={WEBDRIVER_PATH}\n',
            f'MAX_RETRIES={MAX_RETRIES}\n',
            f'HEADLESS={HEADLESS}\n',
        ])


if not os.path.exists('.env') and not os.path.exists('../.env'):
    WEBDRIVER_PATH = 'chromedriver.exe'
    MAX_RETRIES = '10'
    HEADLESS = 'true'
    update_config()
    dotenv.load_dotenv()
else:
    dotenv.load_dotenv()
    WEBDRIVER_PATH = os.environ.get('WEBDRIVER_PATH')
    MAX_RETRIES = int(os.environ.get('MAX_RETRIES') or 0)
    HEADLESS = os.environ.get('HEADLESS').lower() == 'true'


def get_file_write_mode(filename):
    if os.path.exists(filename):
        return 'a'
    return 'w'


class State:
    def __init__(self, filename, directory, default_data=None):
        self.filename = os.path.join(directory, filename)
        self.data = default_data if default_data else dict()
        if not os.path.exists(self.filename):
            self.write()
        else:
            self.update()

    def update(self):
        with open(self.filename, 'r', encoding='utf-8') as state_file:
            for row in state_file.readlines():
                row = row.strip()
                if not row:
                    continue
                row = row.split('=')
                self.data[row[0]] = '='.join(row[1:]) if len(row) > 1 else ''
        self.write()

    def set_data(self, data: dict):
        self.data = data

    def write(self):
        with open(self.filename, 'w') as state_file:
            if self.data:
                for keyval in self.data.items():
                    state_file.write('='.join(map(str, keyval)) + '\n')

    def has_data(self):
        return bool(self.data)

    def reset(self):
        open(self.filename, 'w').close()

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, item):
        return self.data[item] if item in self.data else None

