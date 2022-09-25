import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

docID = []

cred = credentials.Certificate("IOTSHA.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


def DocumentID():
    docs = db.collection(u'Relay12345').stream()
    for doc in docs:
        docID.append(doc.id)


DocumentID()

for i in docID:
    print(i)
    firestore.client().collection(u'Relay12345').document(i).update(
        {'isTransient': False})
