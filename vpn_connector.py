import asyncio
import http.client
import os
import random
import sys
from asyncio import subprocess
from time import sleep

import settings


async def stop():
    if 'win32' == sys.platform:
        proc = await subprocess.create_subprocess_exec('taskkill', '/f', '/im', 'openvpn.exe')
    else:
        proc = await subprocess.create_subprocess_exec('killall', 'openvpn')
    await proc.wait()


async def reconnect():
    # УБИВАЕМ ПРОЦЕСС VPN
    await stop()
    # Получаем возможные конфигурации
    vpn_configures = [i for i in os.listdir('openvpn-configurations') if
                      ('windows' if sys.platform == 'win32' else 'linux') in i]
    while get_ip_info() == first_ip:
        conf = random.choice(vpn_configures)
        # Запускаем процесс подключения к VPN
        await subprocess.create_subprocess_shell(
            settings.OPENVPN + ' --config openvpn-configurations/' + conf,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        sleep(20)


def get_ip_info():
    try:
        conn = http.client.HTTPConnection('ifconfig.me')
        conn.request('GET', '/ip')
        sleep(1)
        return conn.getresponse().read()[:-1]
    except:
        return get_ip_info()


first_ip = get_ip_info()

if __name__ == '__main__':
    asyncio.run(stop())
    sleep(300)
    try:
        while True:
            asyncio.run(reconnect())
            sleep(300)
    finally:
        asyncio.run(stop())
