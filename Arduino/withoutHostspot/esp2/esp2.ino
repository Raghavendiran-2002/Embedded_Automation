#include <ArduinoJson.h>
#include <EEPROM.h>
#include <WiFi.h>
#include <PubSubClient.h>

#define WIFISSID "Raghavendiran"
#define PWD "apple@5g"
//#define WIFISSID "BIRAC_API"
//#define PWD "10267042"
#define Mqtt_username "elab"
#define Mqtt_password "2024"
const char *mqtt_server = "192.168.1.10";
//const char *mqtt_server = "192.168.0.110"; //for iPhone wireless lan
const char *device_id = "esp32-1";
char message_buff[160];

WiFiClient espClient;
PubSubClient client(espClient);

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
//    const char* ID = doc["deviceUID"];
//    bool State  = doc["state"];

//    const char* devicePath = doc["devicePath"]; // "esp1"
  bool state = doc["state"]; // false
  const char* deviceUID = doc["deviceUID"]; // "uid4"
    
  if (strcmp(deviceUID, "e2r1") == 0){
    if (state == true){
      Serial.println("relay1 off");
      digitalWrite(2, LOW);
    }
    else {
      digitalWrite(2, HIGH);
      Serial.println("relay1 on");
    }
  }
  else if (strcmp(deviceUID, "e2r2") == 0) {
    if (state == true){
      Serial.println("relay2 off");
      digitalWrite(4, LOW);
    }
    else {
      digitalWrite(4, HIGH);
      Serial.println("relay2 on");
    }
  }
  else if (strcmp(deviceUID, "e2r3") == 0) {
    if (state == true){
      Serial.println("relay3 off");
      digitalWrite(12, LOW);
    }
    else {
      digitalWrite(12, HIGH);
      Serial.println("relay3 on");
    } 
  }
  else if(strcmp(deviceUID, "e2r4") == 0) {
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

void reconnect()
{
  while (!client.connected())
  {
    Serial.print("Attempting MQTT connection...");
    if (client.connect(device_id, Mqtt_username, Mqtt_password))
    { 
    Serial.println("connected");
    client.publish("req", "RequestingData");
    client.subscribe("esp2");
    client.subscribe("req");
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
  pinMode(1, OUTPUT);
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
//  pinMode(5, OUTPUT);
//  pinMode(6, OUTPUT);
//  pinMode(7, OUTPUT);
//  pinMode(8, OUTPUT);
  pinMode(12, OUTPUT);
  pinMode(14, OUTPUT);
  digitalWrite(2, HIGH);
  digitalWrite(4, HIGH);
  digitalWrite(12, HIGH);
  digitalWrite(14, HIGH);
  Serial.begin(115200);
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
  client.setCallback(callback);
  
}

void loop()
{
  if (!client.connected())
  {
    reconnect();
  }
  client.loop();
}
