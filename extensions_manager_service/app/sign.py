import os
import sys
import zipfile
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

def create_key():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    with open('private.pem', 'wb') as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,  # Изменено на PKCS8
            encryption_algorithm=serialization.NoEncryption()
        ))

    return private_key

def create_zip(extension_dir):
    zip_file = f"{extension_dir}.zip"
    with zipfile.ZipFile(zip_file, 'w') as z:
        for root, dirs, files in os.walk(extension_dir):
            for file in files:
                z.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), extension_dir))
    # Проверка содержимого ZIP
    with zipfile.ZipFile(zip_file, 'r') as z:
        print("Содержимое ZIP-файла:", z.namelist())
    return zip_file

def sign_data(zip_file, private_key):
    with open(zip_file, 'rb') as f:
        zip_data = f.read()

    signature = private_key.sign(
        zip_data,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return signature

def create_crx(extension_dir, zip_file, private_key, signature):
    crx_file = f"{extension_dir}.crx"
    public_key = private_key.public_key()
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with open(crx_file, 'wb') as f:
        # Запись заголовка
        f.write(b'Cr24')  # Магическое число
        f.write(b'\x03\x00\x00\x00')  # Версия (3)
        f.write(len(public_key_bytes).to_bytes(4, 'little'))  # Длина публичного ключа
        f.write(len(signature).to_bytes(4, 'little'))  # Длина подписи

        # Запись публичного ключа и подписи
        f.write(public_key_bytes)
        f.write(signature)

        # Чтение и запись zip данных
        with open(zip_file, 'rb') as z:
            zip_data = z.read()
            f.write(zip_data)  # Сначала записываем zip данные

    # Удаление временного zip файла
    os.remove(zip_file)

    # Отладочная информация
    print("CRX файл создан:")
    print(f"  Файл: {crx_file}")
    print(f"  Длина публичного ключа: {len(public_key_bytes)}")
    print(f"  Длина подписи: {len(signature)}")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python pack_extension.py <extension_directory>")
        sys.exit(1)

    extension_directory = sys.argv[1]

    # Создание ключа
    private_key = create_key()

    # Создание zip-архива
    zip_file = create_zip(extension_directory)

    # Подпись zip-архива
    signature = sign_data(zip_file, private_key)

    # Создание CRX файла
    create_crx(extension_directory, zip_file, private_key, signature)
