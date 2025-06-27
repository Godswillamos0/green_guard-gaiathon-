#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Replace with your network credentials
const char* ssid = "esp8266";
const char* password = "qwertyuiop";

#define MQ_1_PIN 32   // MQ-135 analog
#define MQ2_PIN 34    // MQ-2 analog
#define buzzer_pin 25 // Buzzer pin

LiquidCrystal_I2C lcd(0x27, 16, 2);

const int MQ2_THRESHOLD = 1200;
const int MQ135_THRESHOLD = 1200;

void connectToWiFi() {
  Serial.print("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConnected to WiFi");
  } else {
    Serial.println("\nFailed to connect to WiFi");
  }
}

String getStatusLevel(int mq2, int mq135) {
  int avg = (mq2 + mq135) / 2;

  if (mq135<900 ) return "Excellent";
  else if (mq135<1100 ) return "Good";
  else if (mq135<1250 ) return "Moderate";
  else if (mq135<1300 ) return "Poor";
  else return "Dangerous";
}

String getTimeStamp() {
  time_t now;
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    return "unknown";
  }
  char buffer[30];
  strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%S", &timeinfo);
  return String(buffer);
}

void sendToServer(int c1, int c2, const String& status) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin("https://green-guard-gaiathon.onrender.com/esp/send_data");
    http.addHeader("Content-Type", "application/json");

    String payload = "{\"carbon_index1\": " + String(c1) + 
                     ", \"carbon_index2\": " + String(c2) + 
                     ", \"status\": \"" + status + 
                     "\", \"time_stamp\": \"" + getTimeStamp() + "\"}";

    int httpResponseCode = http.POST(payload);
    Serial.print("POST Status Code: ");
    Serial.println(httpResponseCode);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Response: " + response);
    }

    http.end();
  } else {
    Serial.println("WiFi not connected, skipping POST.");
  }
}

void setup() {
  Serial.begin(115200);
  lcd.init();
  lcd.backlight();
  pinMode(buzzer_pin, OUTPUT);

  lcd.setCursor(0, 0);
  lcd.print("Green Guard");
  delay(2000);
  lcd.clear();

  connectToWiFi();

  // Optional: sync time if timestamp needed
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");

  lcd.setCursor(0, 0);
  lcd.print("System Ready");
  delay(1000);
  lcd.clear();
}

void loop() {
  int carbon_index1 = analogRead(MQ_1_PIN);
  int carbon_index2 = analogRead(MQ2_PIN);

  float voltageMQ135 = carbon_index1 * (3.3 / 4095.0);
  float voltageMQ2 = carbon_index2 * (3.3 / 4095.0);

  Serial.printf("MQ-135 | Raw: %d | V: %.2f V\n", carbon_index1, voltageMQ135);
  Serial.printf("MQ-2   | Raw: %d | V: %.2f V\n", carbon_index2, voltageMQ2);

  String status = getStatusLevel(carbon_index2, carbon_index1);

  // LCD Display
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Status: " + status);

  lcd.setCursor(0, 1);
  if (status == "Dangerous") {
    lcd.print("High Carbon Level");
    digitalWrite(buzzer_pin, HIGH);
    delay(1000);
    digitalWrite(buzzer_pin, LOW);
  } else if (status == "Poor") {
    lcd.print("Unhealthy Emission");
    digitalWrite(buzzer_pin, HIGH);
    delay(300);
    digitalWrite(buzzer_pin, LOW);
  } else if (status == "Moderate") {
    lcd.print("Keep Monitoring");
  } else if (status == "Good") {
    lcd.print("Carbon Level Safe");
  } else if (status == "Excellent") {
    lcd.print("You're in the Green!");
  }

  sendToServer(carbon_index1, carbon_index2, status);

  Serial.println("-------------------------------");
  delay(2000);  // 2 sec delay before next loop
}

