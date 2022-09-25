import sqlite3

conn = sqlite3.connect('E-Lab.db')
print("Opened database successfully")

conn.execute('''CREATE TABLE IF NOT EXISTS HomeAutomation(deviceUID TEXT NOT NULL,parentEsp TEXT NOT NULL,targetState BOOL NOT NULL,actualState BOOL NOT NULL,isTransient BOOL NOT NULL,TimeNow DATETIME DEFAULT CURRENT_TIMESTAMP, UNIQUE(deviceUID));''')
print("Table created successfully")


# {'targetState': True, 'deviceName': 'fan2', 'isTransient': False,
#  'actualState': False, 'parentEsp': 'esp2', 'devicePath': 'esp2/relay4', 'deviceUID': 'e2r4'}
# docID = CdYzUXQPHAsCmk8FMKk1
conn.close()
