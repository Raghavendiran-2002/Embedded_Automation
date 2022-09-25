import sqlite3
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import threading
import time


start_time = time.time()
cred = credentials.Certificate("IOTSHA.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

DATABASE_FILE = 'LiveData.db'
conn = sqlite3.connect(DATABASE_FILE, check_same_thread=False)
conn.execute('''CREATE TABLE IF NOT EXISTS LiveData(deviceUID TEXT NOT NULL,parentEsp TEXT NOT NULL,targetState BOOL NOT NULL,actualState BOOL NOT NULL,isTransient BOOL NOT NULL,TimeNow DATETIME DEFAULT CURRENT_TIMESTAMP, UNIQUE(deviceUID));''')


def DataFromFirestore():
    docs = db.collection(u'Relay12345').stream()
    for doc in docs:
        docDict = doc.to_dict()
        Insert_Previous_DeviceStatus(docDict["deviceUID"], docDict["parentEsp"],
                                     docDict["targetState"], docDict["actualState"], docDict["isTransient"])
    conn.commit()


def Insert_Previous_DeviceStatus(DeviceID, parentNode, targetstate, actualstate, istransient):
    # Initially Inserts data to sqlite
    data1 = (DeviceID, parentNode, targetstate, actualstate, istransient)
    # data2 = (parentNode, targetstate, actualstate, istransient, DeviceID)
    sql1 = "INSERT OR IGNORE INTO LiveData(deviceUID,parentEsp,targetState,actualState,isTransient) VALUES (?,?,?,?,?)"
    # sql2 = "UPDATE LiveData set parentEsp=?, targetState=?, actualState=?, isTransient=?, TimeNow=DATETIME CURRENT_TIMESTAMP where deviceUID = ?"
    try:
        conn.execute(sql1, data1)
        # conn.execute(sql2, data2)
    except sqlite3.OperationalError as e:
        pass


testThread = threading.Thread(target=DataFromFirestore)
testThread.start()

# Infinity Loop
# while True:
#     DataFromFirestore()
#     conn.commit()

print("--- %s seconds ---" % (time.time() - start_time))
