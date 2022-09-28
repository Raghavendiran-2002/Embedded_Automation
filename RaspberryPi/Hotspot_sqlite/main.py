

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
import sqlite3
import threading
from paho.mqtt import client as mqtt
import urllib.request


DATABASE_FILE = 'LiveData.db'
conn = sqlite3.connect(DATABASE_FILE, check_same_thread=False)
IP_ADDRESS = "192.168.4.150"
username = 'elab'
password = '2024'
DocID_UID = {}  # key ["deviceUID"] Value ["DocID"]


client = mqtt.Client()
client.username_pw_set(username, password)
client.connect(IP_ADDRESS, 1883, 60)

cred = credentials.Certificate("IOTSHA.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


def internetConnectionCheck(host='https://google.com'):
    # Checks Internet Connection
    try:
        urllib.request.urlopen(host)
        return True
    except:
        return False


def updateRealTimeData(DeviceID, parentNode, targetstate, actualstate, istransient):
    # Calls every time data is when relay is turned on or off
    # Updates all the data to LocalDB(SQLite)
    data = (parentNode, targetstate, actualstate, istransient, DeviceID)
    sql = "UPDATE LiveData set parentEsp=?, targetState=?, actualState=?, isTransient=?  where deviceUID = ?"
    conn.execute(sql, data)
    conn.commit()


def updateIsTransient(DeviceID, istransient):
    # Updates istransient state in LocalDB(SQLite)
    data = (istransient, DeviceID)
    sql = "UPDATE LiveData set isTransient=? where deviceUID = ?"
    conn.execute(sql, data)
    conn.commit()


def publishChangesToEsp(docs_snapshot):
    # called only for isTransient true docs
    # refer documentation
    for doc in docs_snapshot:
        # doc.document used here as syntax when using changed docs
        # (changed docs only recieved from listener, check on_snapshot code)
        docDict = doc.document.to_dict()
        jsonDoc = {
            "state": docDict["targetState"], "deviceUID": docDict["deviceUID"], "parentEsp": docDict["parentEsp"]}
        # UpdateIsTransient(docDict["deviceUID"], docDict["isTransient"])
        UpdateSQLThread = threading.Thread(target=updateIsTransient, args=(
            docDict["deviceUID"], docDict["isTransient"]), daemon=True)
        # threading here as multiple requests get queued waiting for the prev on_snapshot call to complete
        UpdateSQLThread.start()

        client.publish(docDict["parentEsp"], json.dumps(jsonDoc),  qos=1)


def fetchdocumentID():
    # Fetches Document ID from Firestore
    docs = db.collection(u'Relay12345').stream()
    for doc in docs:
        docDict = doc.to_dict()
        # Stores (deviceUID = DocID) as Dictonary
        DocID_UID[docDict["deviceUID"]] = doc.id


def publishInitStatesToEsp(docs_snapshot):
    # called only for isTransient false docs
    # refer documentation
    for doc in docs_snapshot:
        docDict = doc.to_dict()
        # Stores (deviceUID = DocID) as Dictonary
        print(docDict)  # Prints Document Data as JSON
        jsonDoc = {
            "state": docDict["targetState"], "deviceUID": docDict["deviceUID"], "parentEsp": docDict["parentEsp"]}
        client.publish(docDict["parentEsp"], json.dumps(jsonDoc),  qos=1)


def on_snapshot(docs_snapshot, changes, read_time):
    # only sending over docs with changes from prev state, as firebase client sdk
    # gives all docs (changed one from firebase + remaining all cached ones)
    testThread = threading.Thread(target=publishChangesToEsp, args=(changes,))
    # threading here as multiple requests get queued waiting for the prev on_snapshot call to complete
    testThread.start()


def getFirebaseDocsOnStartupIndividualESP(parentEsp):
    # only isTransient false docs here as snapshot listener will take care of isTransient true docs
    snapshot = db.collection("Relay12345").where(
        u'isTransient', u'==', False).where(u'parentEsp', u'==', parentEsp).get()
    publishInitStatesToEsp(snapshot)


def getFirebaseDocsOnStartup():
    # only isTransient false docs here as snapshot listener will take care of isTransient true docs
    snapshot = db.collection("Relay12345").where(
        u'isTransient', u'==', False).get()
    publishInitStatesToEsp(snapshot)


def mqtt_on_connection_init(client, userdata, flags, rc):
    # initializes MQTT
    print("MQTT Connected, Initializing Firebase...")


def on_message_recieved(client, userdata, msg):
    # when esp32 restart. It get previous data from firestore
    if((msg.topic) == "req"):
        onTransientListener()
        getFirebaseDocsOnStartupIndividualESP(msg.payload.decode())
    elif(msg.topic == "controller/response" and len(msg.payload.decode()) >= 35):
        # json.loads - convert JSON string to python dict
        responseDict = json.loads(msg.payload.decode())
        print("{} : {}".format(
            responseDict["deviceUID"], "ON" if(responseDict['state']) else "OFF"))
        db.collection("Relay12345").document(DocID_UID[responseDict["deviceUID"]]).update(
            {'isTransient': False, 'actualState': responseDict['state']})

        updateDataThread = threading.Thread(target=updateRealTimeData, args=(responseDict["deviceUID"], responseDict["parentEsp"],
                                                                             responseDict["state"], responseDict["state"], False), daemon=True)
        updateDataThread.start()  # 'conn.commit()' to avoid sqlException
        # print("response",  json.loads(msg.payload.decode()))
    elif((msg.topic) == "local/response"):
        # This condition is trigger when manual switch is used
        x = json.loads(msg.payload.decode())
        db.collection("Relay12345").document(DocID_UID[x["deviceUID"]]).update(
            {'targetState': x['state'], 'actualState': x['state']})
        print(x["deviceUID"],  " : ", {x['state']})


def onTransientListener():
    # below query fetches isTransient true docs to be published
    # thus, to fetch all deviceDocs on startup, getFirebaseDocsOnStartup is used
    # this is done so as to prevent a response doc (where isTransient will be false) from triggering the listener
    db.collection(u'Relay12345').where(u'isTransient',
                                       u'==', True).on_snapshot(on_snapshot)
    # positioning getFirebaseDocsOnStartup() below on_snapshot as on_snapshot's already threaded (right?)
    # and thus both can run in parallel
    # getFirebaseDocsOnStartup()

# ******************************main******************************


client.subscribe("controller/response")
client.subscribe("req")
client.subscribe("local/response")
print("Internet Connected" if internetConnectionCheck() else "No Internet!")
fetchdocumentID()  # Stores DocID

onTransientListener()
client.on_connect = mqtt_on_connection_init
client.on_message = on_message_recieved

client.loop_forever()

conn.close()
