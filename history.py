import os
import sqlite3
from datetime import datetime, timedelta
import shutil
from prettytable import PrettyTable

history_db = os.path.expanduser(r'~\AppData\Local\Google\Chrome\User Data\Default\History')
temp_history_db = os.path.expanduser(r'~\chrome_temp_history.db')
shutil.copy2(history_db, temp_history_db)

def chrome_time_to_readable(chrome_time):
    return datetime(1601, 1, 1) + timedelta(microseconds=chrome_time)

conn = sqlite3.connect(temp_history_db)
cursor = conn.cursor()
cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls ORDER BY last_visit_time DESC")

table = PrettyTable()
table.field_names = ["URL", "Title", "Visit Count", "Last Visit Time"]
table.align["URL"] = "l"
table.align["Title"] = "l"
table.align["Visit Count"] = "r"
table.align["Last Visit Time"] = "l"

for url, title, visit_count, last_visit_time in cursor.fetchall():
    table.add_row([url, title, visit_count, chrome_time_to_readable(last_visit_time)])

conn.close()
os.remove(temp_history_db)

print(table)
