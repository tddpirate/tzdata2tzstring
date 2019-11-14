///////////////////////////////////////////////////////////////////////////////////
//
// ESP8266_auto_timezone_demo.ino
// An ESP8266 application demonstrating automatic timezone handling for low-memory
// IoT devices.
//
// Copyright (C)2019  Omer ZAK
//
// This file is part of ESP8266_auto_timezone_demo
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.
//
///////////////////////////////////////////////////////////////////////////////////

#include <ESP8266WiFi.h>          //https://github.com/esp8266/Arduino
#include "get_tz_string.h"

//needed for library
#include <DNSServer.h>
#include <ESP8266WebServer.h>
#include <WiFiManager.h>          //https://github.com/tzapu/WiFiManager

//WiFiManager
const char *AP_SSID     PROGMEM = "MySSID";
const char *AP_PASSWORD PROGMEM = "MyPasswd";
//WiFiManager

#define NTP_UPDATE_INTERVAL 24*3600     // Update from NTP once per 24 hours.
//const int WIFI_TIMEOUT = 100;         // WiFi timeout set to 100 seconds.


// callback notifying us of the need to configure AP
void configModeCallback (WiFiManager *myWiFiManager) {
  Serial.println(F("Entered config mode"));
  Serial.println(WiFi.softAPIP());

  Serial.println(myWiFiManager->getConfigPortalSSID());
}

/*
// the timeout argument is in seconds.
// Return true if connection is successful, false otherwise.
// It is assumed that the WiFi credentials are already loaded into the system, perhaps by another sketch.
bool connectWiFi(int timeout) {
  WiFi.mode(WIFI_STA);
  WiFi.begin(); // We assume that the WiFi credentials are already set.
  for (int loopindex = timeout; loopindex > 0; --loopindex) {
    if (WiFi.status() == WL_CONNECTED) {
      return true;
    }
    delay(1000);
    Serial.print(".");
  }
  return false;
}
*/

//flag for saving data
bool shouldSaveConfig = false;

//callback notifying us of the need to save config
void saveConfigCallback () {
  Serial.println(F("Should save config"));
  shouldSaveConfig = true;
}


void setup() {
  Serial.begin(115200);
  Serial.println();

  //WiFiManager
  //Local intialization. Once its business is done, there is no need to keep it around
  WiFiManager wifiManager;

  // set config mode callback
  wifiManager.setAPCallback(configModeCallback);
  //set config save notify callback
  wifiManager.setSaveConfigCallback(saveConfigCallback);

  //reset settings - for testing
  //wifiManager.resetSettings();

  //set minimum quality of signal so it ignores AP's under that quality
  //defaults to 8%
  wifiManager.setMinimumSignalQuality();
  
  //sets timeout until configuration portal gets turned off
  //useful to make it all retry or go to sleep
  //in seconds
  //wifiManager.setTimeout(120);

  //fetches ssid and pass and tries to connect
  //if it does not connect it starts an access point with the specified name (AP_SSID)
  //and goes into a blocking loop awaiting configuration
  if (!wifiManager.autoConnect(String(AP_SSID).c_str(), String(AP_PASSWORD).c_str())) {
    Serial.println(F("failed to connect and hit timeout"));
    delay(3000);
    //reset and try again, or maybe put it to deep sleep
    ESP.reset();
    delay(5000);
  }

  //if you get here you have connected to the WiFi
  Serial.println(F("connected...yeey :)"));

  //NTP
  configTime(0, 0, String(F("pool.ntp.org")).c_str());
  //NTP

  Serial.println(F("local ip"));
  Serial.println(WiFi.localIP());
  Serial.println(WiFi.gatewayIP());
  Serial.println(WiFi.subnetMask());

  setenv("TZ", get_tz_string(), 1);
}

//NTP
time_t now;
time_t prev_now = 0;
time_t last_ntp_time = 0;
bool ntp_update_not_done = true;
const char timeformat[] PROGMEM = "%2d:%02d:%02d";
//NTP

void loop() {
  now = time(nullptr);
  if (ntp_update_not_done || ((now - last_ntp_time) > NTP_UPDATE_INTERVAL)) {
    // Get updated time from NTP
    configTime(0, 0, String(F("pool.ntp.org")).c_str());
    ntp_update_not_done = false;

    Serial.println(F("--NTP update--"));
    Serial.print(F("now=")); Serial.print(now); Serial.print(F(" last_ntp_time=")); Serial.println(last_ntp_time);

    /*
    connectWiFi(WIFI_TIMEOUT);
    Serial.flush();
    */
    now = time(nullptr);
    last_ntp_time = now;
  }
  if (now != prev_now) {
    tm *unpacked_now = localtime(&now); //gmtime(&now_tz) for manual time setting

    Serial.print(F("now: ")); Serial.print(now); Serial.print(F(" <- "));Serial.print(prev_now);
    Serial.print(F("   "));
    Serial.printf_P(timeformat, unpacked_now->tm_hour, unpacked_now->tm_min, unpacked_now->tm_sec);
    Serial.println();
    Serial.flush();

    prev_now = now;
  }
  delay(100);
}

// End of ESP8266_auto_timezone_demo.ino
