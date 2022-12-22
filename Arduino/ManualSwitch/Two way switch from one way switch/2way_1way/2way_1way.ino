#include <PubSubClient.h>
#include <WiFi.h>

#define WIFISSID "RPiHotspot"
#define PWD "1234567890"

const char *mqtt_server = "192.168.4.150";
const char *device_id = "esp32";

#define Mqtt_username "elab"
#define Mqtt_password "2024"

// it wil set the static IP address to 192, 168, 1, 184
IPAddress local_IP(192, 168, 4, 153);
//it wil set the gateway static IP address to 192, 168, 1,1
IPAddress gateway(192, 168, 4, 1);
// Following three settings are optional
IPAddress subnet(255, 255, 255, 0);
IPAddress primaryDNS(8, 8, 8, 8);
IPAddress secondaryDNS(8, 8, 4, 4);


WiFiClient espClient;
PubSubClient client(espClient);

void setup()
{
    Serial.begin(115200);
    if (!WiFi.config(local_IP, gateway, subnet, primaryDNS, secondaryDNS)) {
    Serial.println("STA Failed to configure");
    }
    WiFi.begin(WIFISSID, PWD);
    Serial.print("Connecting to Wi-Fi");
    while (WiFi.status() != WL_CONNECTED)
    {
        Serial.println(".");
        delay(300);
    }
    client.setServer(mqtt_server, 1883);
    client.setCallback(callback);
    pinMode(4, INPUT_PULLUP);
    pinMode(5, OUTPUT);
}

int prevSwitchState = -1;
bool alternateTerminals = false;
bool normalPullupLogic = true;

void loop()
{

    if (!client.connected())
    {
        reconnect();
    }
    updateManualSwitchState();
    client.loop();
}

void updateManualSwitchState()
{

    int currentSwitchState = digitalRead(4);
    if (currentSwitchState != prevSwitchState)
    {
        prevSwitchState = currentSwitchState;
        if (alternateTerminals == true)
        {
            normalPullupLogic = !normalPullupLogic;
            alternateTerminals = false;
        }

        if (normalPullupLogic && currentSwitchState)
        {
            digitalWrite(5, LOW);
        }
        else if (normalPullupLogic && !currentSwitchState)
        {
            digitalWrite(5, HIGH);
        }
        else if (!normalPullupLogic && currentSwitchState)
        {
            digitalWrite(5, HIGH);
        }
        else
        {
            digitalWrite(5, LOW);
        }
    }
}

void callback(char *topic, byte *payload, unsigned int length)
{
    char recv = (char)payload[0];
    if ((recv == '1' && digitalRead(4)) || (recv == '0' && !digitalRead(4)))
    {
        Serial.println("Alternated");
        alternateTerminals = true;
    }
    if (recv == '1')
    {
        digitalWrite(5, HIGH);
    }
    else
    {
        digitalWrite(5, LOW);
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
            client.publish("initi/msg", "here");
            client.subscribe("rem/switch");
        }
        else
        {
            Serial.print("failed, rc=");
            Serial.print(client.state());
            Serial.println(" try again in 2.5 seconds");
            delay(2500);
        }
    }
}