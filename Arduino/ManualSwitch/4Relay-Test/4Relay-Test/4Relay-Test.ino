#include <ArduinoJson.h>
#include <EEPROM.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ezButton.h>

// #define WIFISSID "Raghavendiran"
//#define PWD "10267042"
// #define WIFISSID "RPiHotspot"
// #define PWD "1234567890"
#define WIFISSID "Raghavendiran"
#define PWD "apple@5g"
#define Mqtt_username "elab"
#define Mqtt_password "2024"
//const char *mqtt_server = "localhost";
const char *mqtt_server = "192.168.1.4"; //for iPhone wireless lan
const char *device_id = "esp32";
char message_buff[160];

// // it wil set the static IP address to 192, 168, 1, 184
// IPAddress local_IP(192, 168, 4, 153);
// //it wil set the gateway static IP address to 192, 168, 1,1
// IPAddress gateway(192, 168, 4, 1);
// // Following three settings are optional
// IPAddress subnet(255, 255, 255, 0);
// IPAddress primaryDNS(8, 8, 8, 8);
// IPAddress secondaryDNS(8, 8, 4, 4);


WiFiClient espClient;
PubSubClient client(espClient);

// ezButton SwitchPin1(32);
// ezButton SwitchPin2(33);
// ezButton SwitchPin3(34);
// ezButton SwitchPin4(35);
int r1 = LOW;
int r2 = LOW;
int r3 = LOW;
int r4 = LOW;


#define RelayPin1 2  //D1
#define RelayPin2 4  //D2
#define RelayPin3 12  //D5
#define RelayPin4 14  //D6

#define SwitchPin1 32  //D32
#define SwitchPin2 33  //D33
#define SwitchPin3 34  //D34
#define SwitchPin4 35  //D35

int prevSwitchState1 = -1;
int prevSwitchState2 = -1;
int prevSwitchState3 = -1;
int prevSwitchState4 = -1;

bool alternateTerminals1 = false;
bool alternateTerminals2 = false;
bool alternateTerminals3 = false;
bool alternateTerminals4 = false;

bool normalPullupLogic1 = true;
bool normalPullupLogic2 = true;
bool normalPullupLogic3 = true;
bool normalPullupLogic4 = true;



void callback(char *topic, byte *payload, unsigned int length){
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.println("] ");

  char message[length];
    int i;
    for (i = 0; i<length; i++) {
      message[i] = ((char)payload[i]);
    }
    message[length] = '\0';
    Serial.println(message);
    client.publish("controller/response", message);
    DynamicJsonDocument doc(64); //32 bytes calculated for worst case without any overhead
                               //for particular use case using ArduinoJson Assistant
    deserializeJson(doc, message);
    bool state = doc["state"]; // false
    const char* deviceUID = doc["deviceUID"]; // "uid4"
    const char* parentEsp = doc["parentEsp"];

    if (strcmp(deviceUID, "e1r1") == 0){
      if ((state == true  && digitalRead(SwitchPin1)) || (state == false && !digitalRead(SwitchPin1))){
        Serial.println("Alternated");
        alternateTerminals1 = true;
      }
      if(state == true){
        Serial.println("relay1 on");
        digitalWrite(RelayPin1, HIGH);
      }
      else {
        digitalWrite(RelayPin1, LOW);
        Serial.println("relay1 off");
      }
    }
    else if (strcmp(deviceUID, "e1r2") == 0) {
      if (state == true){
        Serial.println("relay2 off");
        digitalWrite(4, LOW);
      }
      else {
         digitalWrite(4, HIGH);
        Serial.println("relay2 on");
      }
    }
    else if (strcmp(deviceUID, "e1r3") == 0) {
      if (state == true){
        Serial.println("relay3 off");
        digitalWrite(12, LOW);
      }
      else {
        digitalWrite(12, HIGH);
        Serial.println("relay3 on");
     }
  }
  else if(strcmp(deviceUID, "e1r4") == 0) {
      if (state == true){
        Serial.println("relay4 off");
        digitalWrite(14, LOW);
      }
      else {
        digitalWrite(14, HIGH);
        Serial.println("relay4 on");
    }
  }
}
void updateManualSwitchState()
{
    DynamicJsonDocument doc(1024);
    doc["parentEsp"] = "esp1";
    int currentSwitchState = digitalRead(RelayPin1);
    doc["deviceUID"]   = "e1r1";
    if (currentSwitchState != prevSwitchState1)
    {
        prevSwitchState1 = currentSwitchState;
        if (alternateTerminals1 == true)
        {
            normalPullupLogic1 = !normalPullupLogic1;
            alternateTerminals1 = false;
            // doc["state"] = true;
        }

        if (normalPullupLogic1 && currentSwitchState)
        {
            digitalWrite(SwitchPin1, LOW);
            doc["state"] = false;
                        client.publish("local/response", message);

        }
        else if (normalPullupLogic1 && !currentSwitchState)
        {
            digitalWrite(SwitchPin1, HIGH);
            doc["state"] = true;
                        client.publish("local/response", message);

        }
        else if (!normalPullupLogic1 && currentSwitchState)
        {
            digitalWrite(SwitchPin1, HIGH);
            doc["state"] = true;
                        client.publish("local/response", message);

        }
        else
        {
            digitalWrite(SwitchPin1, LOW);
            doc["state"] = false;
            client.publish("local/response", message);
        }
    }
    char message[100];
    serializeJson(doc, message);
    
    serializeJson(doc, Serial);
}

// void PublishLocal(){
//   DynamicJsonDocument doc(1024);
//   doc["parentEsp"] = "esp1";

//   if(SwitchPin1.isPressed()){
//     doc["deviceUID"]   = "e1r1";
//     r1 = !r1;
//     if(r1==0){
//       doc["state"] = false;
//     }
//     else{
//       doc["state"] = true;
//     }
//     digitalWrite(RelayPin1, r1);
//     char message[100];
//     serializeJson(doc, message);
//     client.publish("local/response", message);
//     serializeJson(doc, Serial);
//   }
//   if(SwitchPin2.isPressed()){
//     doc["deviceUID"]   = "e1r2";
//     r2 = !r2;
//     if(r2==0){
//       doc["state"] = false;
//     }
//     else{
//       doc["state"] = true;
//     }
//     digitalWrite(RelayPin2, r2);
//     char message[100];
//     serializeJson(doc, message);
//     client.publish("local/response", message);
//     serializeJson(doc, Serial);
//   }
//   if(SwitchPin3.isPressed()){
//     doc["deviceUID"]   = "e1r3";
//     r3 = !r3;
//     if(r3==0){
//       doc["state"] = false;
//     }
//     else{
//       doc["state"] = true;
//     }
//     digitalWrite(RelayPin3, r3);
//     char message[100];
//     serializeJson(doc, message);
//     client.publish("local/response", message);
//     serializeJson(doc, Serial);
//   }
//   if(SwitchPin4.isPressed()){
//     doc["deviceUID"]   = "e1r4";
//     r4 = !r4;
//     if(r4==0){
//       doc["state"] = false;
//     }
//     else{
//       doc["state"] = true;
//     }
//     digitalWrite(RelayPin4, r4);
//     char message[100];
//     serializeJson(doc, message);
//     client.publish("local/response", message);
//     serializeJson(doc, Serial);
//   }


//   // serializeJson(doc, Serial); // Prints JSON


// }

void reconnect()
{
  while (!client.connected())
  {
    Serial.print("Attempting MQTT connection...");
//    if (client.connect(device_id, "elab", "2024"))
    if (client.connect(device_id, "elab", "2024"))
    {
    Serial.println("connected");
    client.publish("req", "esp1");
    client.subscribe("esp1");
    }
    else
    {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup(){
  pinMode(RelayPin1, OUTPUT);
  pinMode(RelayPin2, OUTPUT);
  pinMode(RelayPin3, OUTPUT);
  pinMode(RelayPin4, OUTPUT);
  // digitalWrite(RelayPin1, LOW);
  // digitalWrite(RelayPin2, HIGH);
  // digitalWrite(RelayPin3, HIGH);
  // digitalWrite(RelayPin4, HIGH);
  pinMode(SwitchPin1, INPUT_PULLUP);
  pinMode(SwitchPin2, INPUT_PULLUP);
  pinMode(SwitchPin3, INPUT_PULLUP);
  pinMode(SwitchPin4, INPUT_PULLUP);

  

  Serial.begin(115200);
  // if (!WiFi.config(local_IP, gateway, subnet, primaryDNS, secondaryDNS)) {
  //   Serial.println("STA Failed to configure");
  // }
  WiFi.begin(WIFISSID, PWD);

  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED){
    Serial.print(".");
    delay(300);
  }
  Serial.println();
  Serial.print("Connected with IP: ");
  Serial.println(WiFi.localIP());
  Serial.println();
  client.setServer(mqtt_server, 1883);
  // client.publish("req", "RequestingData");
  client.setCallback(callback);
}

void loop()
{
  if (!client.connected())
  {
    reconnect();
  }
  // PublishLocal();
  updateManualSwitchState();
  client.loop();
}