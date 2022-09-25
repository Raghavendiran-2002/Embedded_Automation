import sqlite3
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("IOTSHA.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

DATABASE_FILE = 'DocID-Reference.db'
conn = sqlite3.connect(DATABASE_FILE)
conn.execute('''CREATE TABLE IF NOT EXISTS DocReference(docID TEXT NOT NULL ,deviceUID TEXT NOT NULL, UNIQUE(docID,deviceUID));''')


def DocID_DeviceID():
    docs = db.collection(u'Relay12345').stream()
    for doc in docs:
        docDict = doc.to_dict()
        # print(f'{doc.id} => {doc.to_dict()}')
        print(docDict["deviceUID"], " ", doc.id)
        Insert_DocID_DeviceID(doc.id, docDict["deviceUID"])


def Insert_DocID_DeviceID(DocID, DeviceID):
    # Initially Inserts data to sqlite
    data = (DocID, DeviceID)
    sql = "INSERT OR IGNORE INTO DocReference (docID,deviceUID) VALUES (?,?)"
    try:
        conn.execute(sql, data)
    except sqlite3.OperationalError as e:
        pass


DocID_DeviceID()
conn.commit()
