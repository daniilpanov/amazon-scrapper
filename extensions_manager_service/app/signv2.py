import os
import zipfile
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import hashes

def create_zip(extension_dir):
    zip_file = f"{extension_dir}.zip"
    with zipfile.ZipFile(zip_file, 'w') as z:
        for root, dirs, files in os.walk(extension_dir):
            for file in files:
                z.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), extension_dir))
    return zip_file

def sign_data(zip_file, private_key):
    with open(zip_file, 'rb') as f:
        zip_data = f.read()
    signature = private_key.sign(
        zip_data,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return zip_data, signature

def create_crx(extension_dir, private_key, zip_data, signature):
    crx_file = f"{extension_dir}.crx"
    public_key = private_key.public_key()
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with open(crx_file, 'wb') as f:
        f.write(b'Cr24')  # Магическое число
        f.write(b'\x03')  # Версия (3)

        # Записываем длины
        length_of_public_key = len(public_key_bytes)
        length_of_signature = len(signature)

        # Длина открытого ключа
        f.write(length_of_public_key.to_bytes(4, 'little'))
        # Длина подписи
        f.write(length_of_signature.to_bytes(4, 'little'))

        # Записываем открытый ключ
        f.write(public_key_bytes)
        # Записываем подпись
        f.write(signature)
        # Записываем ZIP-данные
        f.write(zip_data)

    print(f"CRX файл создан: {crx_file}")

# Пример использования
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

extension_dir = '~/Projects/amazon-scraper/extensions_local/test'
zip_file = create_zip(extension_dir)
zip_data, signature = sign_data(zip_file, private_key)
create_crx(extension_dir, private_key, zip_data, signature)
