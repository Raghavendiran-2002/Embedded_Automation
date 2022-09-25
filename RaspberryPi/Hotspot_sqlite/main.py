# from heapq import merge
from urllib import response
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
import sqlite3
from time import time
from datetime import datetime
import threading
from paho.mqtt import client as mqtt

DATABASE_FILE = 'E-Lab.db'
conn = sqlite3.connect(DATABASE_FILE)
IP_ADDRESS = "192.168.4.150"
username = 'elab'
password = '2024'
DocID_UID = {}  # key ["deviceUID"] Value ["DocID"]


def InsertRealTimeDate(DeviceID, parentNode, targetstate, actualstate, istransient):
    # Initially Inserts data to sqlite
    data = (DeviceID, parentNode, targetstate, actualstate, istransient)
    sql = "INSERT OR IGNORE INTO HomeAutomation (deviceUID,parentEsp,targetState,actualState,isTransient) VALUES (?,?,?,?,?)"
    try:
        conn.execute(sql, data)
    except sqlite3.OperationalError as e:
        pass
    conn.commit()


def UpdateReaTimeDate(DeviceID, parentNode, targetstate, actualstate, istransient):
    data = (parentNode, targetstate, actualstate, istransient, DeviceID)
    sql = "UPDATE HomeAutomation set parentEsp=?, targetState=?, actualState=?, isTransient=?  where deviceUID = ?"
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
        client.publish(docDict["parentEsp"], json.dumps(jsonDoc))


def DocumentID(docs_snapshot):
    for doc in docs_snapshot:
        docDict = doc.to_dict()
        # Stores (deviceUID = DocID) as Dictonary
        DocID_UID[docDict["deviceUID"]] = doc.id
    # print(DocID_UID)  # Prints Document Data as JSON
    # print(DocID_UID[docDict["deviceUID"]])  # // Prints DocumentID


def publishInitStatesToEsp(docs_snapshot):
    # called only for isTransient false docs
    # refer documentation
    for doc in docs_snapshot:
        docDict = doc.to_dict()
        # Stores (deviceUID = DocID) as Dictonary
        # DocID_UID[docDict["deviceUID"]] = doc.id
        print(docDict)  # Prints Document Data as JSON
        # print(DocID_UID[docDict["deviceUID"]])  # // Prints DocumentID
        InsertRealTimeDate(docDict["deviceUID"], docDict["parentEsp"],
                           docDict["targetState"], docDict["actualState"], docDict["isTransient"])
        # UpdateValue(DocID_UID[docDict["deviceUID"]], doc.id,docDict["parentEsp"], docDict["targetState"])
        jsonDoc = {
            "state": docDict["targetState"], "deviceUID": docDict["deviceUID"], "parentEsp": docDict["parentEsp"]}
        client.publish(docDict["parentEsp"], json.dumps(jsonDoc))
        # InsertValue(docDict["deviceUID"], DocID_UID[docDict["deviceUID"]],
        #             docDict["parentEsp"], docDict["targetState"])


def on_snapshot(docs_snapshot, changes, read_time):
    # only sending over docs with changes from prev state, as firebase client sdk
    # gives all docs (changed one from firebase + remaining all cached ones)
    testThread = threading.Thread(target=publishChangesToEsp, args=(changes,))
    # threading here as multiple requests get queued waiting for the prev on_snapshot call to complete
    testThread.start()


def getFirebaseDocsOnStartup():
    # only isTransient false docs here as snapshot listener will take care of isTransient true docs
    snapshot = db.collection("Relay12345").where(
        u'isTransient', u'==', False).get()
    # Error occurs when isTransient == true .To FIX change it to false
    DocumentID(snapshot)
    publishInitStatesToEsp(snapshot)


def mqtt_on_connection_init(client, userdata, flags, rc):
    print("MQTT Connected, Initializing Firebase...")


def on_message_recieved(client, userdata, msg):
    # when esp32 restart. It get previous data from cloud
    if((msg.topic) == "req" and (msg.payload.decode()) == "RequestingData"):
        getFirebaseDocsOnStartup()
    elif(msg.topic == "controller/response"):
        # print(DocID_UID)
        # json.loads - convert JSON string to python dict
        responseDict = json.loads(msg.payload.decode())
        print(responseDict)
        # print(DocID_UID[responseDict["deviceUID"]])
        db.collection("Relay12345").document(DocID_UID[responseDict["deviceUID"]]).update(
            {'isTransient': False, 'actualState': responseDict['state']})
        UpdateReaTimeDate(responseDict["deviceUID"], responseDict["parentEsp"],
                          responseDict["state"], responseDict["state"], False)
        print("response",  json.loads(msg.payload.decode()))

# ******************************main******************************


# ConnectDatabase()
client = mqtt.Client()
client.username_pw_set(username, password)
client.connect(IP_ADDRESS, 1883, 60)
# client.connect("localhost", 1883, 60)
# client.subscribe("esp1")
client.subscribe("controller/response")
client.subscribe("req")
cred = credentials.Certificate("IOTSHA.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# below query fetches isTransient true docs to be published
# thus, to fetch all deviceDocs on startup, getFirebaseDocsOnStartup is used
# this is done so as to prevent a response doc (where isTransient will be false) from triggering the listener
db.collection(u'Relay12345').where(
    u'isTransient', u'==', True).on_snapshot(on_snapshot)
# positioning getFirebaseDocsOnStartup() below on_snapshot as on_snapshot's already threaded (right?)
# and thus both can run in parallel
getFirebaseDocsOnStartup()

client.on_connect = mqtt_on_connection_init
client.on_message = on_message_recieved

client.loop_forever()
conn.close()
