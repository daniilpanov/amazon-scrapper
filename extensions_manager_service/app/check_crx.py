import sys

def check_crx_header(crx_file):
    with open(crx_file, 'rb') as f:
        magic = f.read(4)
        if magic != b'Cr24':
            print("Неверный заголовок CRX.")
            return

        version = f.read(1)
        header_length = int.from_bytes(f.read(4), 'little')
        zip_length = int.from_bytes(f.read(4), 'little')
        public_key_length = int.from_bytes(f.read(4), 'little')
        signature_length = int.from_bytes(f.read(4), 'little')

        print("Информация о заголовке CRX:")
        print(f"  Магическое число: {magic}")
        print(f"  Версия: {version[0]}")
        print(f"  Длина заголовка: {header_length}")
        print(f"  Длина zip: {zip_length}")
        print(f"  Длина публичного ключа: {public_key_length}")
        print(f"  Длина подписи: {signature_length}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python check_crx_header.py <crx_file>")
        sys.exit(1)

    crx_file = sys.argv[1]
    check_crx_header(crx_file)
