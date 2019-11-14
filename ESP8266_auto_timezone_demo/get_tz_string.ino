///////////////////////////////////////////////////////////////////////////////////
// Retrieve the tz_string corresponding to the user's IP
// This file is part of ESP8266_auto_timezone_demo
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
// Before using this code:
// 1. Edit the URLs in the calls to get_https_payload() to fit your use case.
//    For the first payload, use a IP to timezone service (a list can be found
//    in get_tz_string.h).
//    For the second payload, set up a small website and use its URL as an
//    argument to get_https_payload().
// 2. Add (if necessary) the code to extract the timezone name from the XML
//    or JSON returned from the website.
//    If you use Timezone API, you need to make only one get_https_payload() call.
///////////////////////////////////////////////////////////////////////////////////

#include "get_tz_string.h"
#include "urlencoder.h"

#include <ESP8266HTTPClient.h>
#include <WiFiClientSecureBearSSL.h>


String payload((char *)0);

// The result is stored in String payload.
int get_https_payload(String full_url) {
    std::unique_ptr<BearSSL::WiFiClientSecure>client(new BearSSL::WiFiClientSecure);

    client->setInsecure();

    HTTPClient https;

    Serial.print(F("[HTTPS] begin...\n"));
    if (https.begin(*client, full_url)) {  // HTTPS

      Serial.print(F("[HTTPS] GET... from "));
      Serial.print(full_url);
      Serial.print(F("\n"));
      // start connection and send HTTP header
      int httpCode = https.GET();

      // httpCode will be negative on error
      if (httpCode > 0) {
        // HTTP header has been send and Server response header has been handled
        Serial.printf_P(PSTR("[HTTPS] GET... code: %d\n"), httpCode);

        // file found at server
        if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_MOVED_PERMANENTLY) {
          payload = https.getString();
          Serial.println(payload);
        }
      } else {
        Serial.printf_P(PSTR("[HTTPS] GET... failed, error: %s\n"), https.errorToString(httpCode).c_str());
      }

      https.end();
    } else {
      Serial.printf_P(PSTR("[HTTPS] Unable to connect\n"));
    }
    return NULL;
}

const char *get_tz_string() {
  //#define TEST_URLENCODE
  #ifdef TEST_URLENCODE
  String test_argument(F("a1/b2 comma:, tilde:~"));
  String test_value((char *)0);
  urlencode(test_argument, test_value);
  Serial.print(F("*** TEST: urlencode('a1/b2 comma:, tilde:~') should be 'a1%2fb2+comma%3a%2c+tilde%3a~' ***\n"));
  Serial.printf_P(PSTR("*** Actual value: %s ***\n"), test_value.c_str());
  #endif /* TEST_URLENCODE */

  int retval = get_https_payload(F("https://get_timezone.example.com/"));
  if (retval != 0) {
     return NULL;  // Failure
  }
  // Here extract the timezone name from payload. Subsequent code assumes that the timezone name is again in payload.
  String urlencoded_payload((char *)0);  // I want to free the memory at end of this function.
  urlencode(payload, urlencoded_payload);
  retval = get_https_payload(String(String(F("https://timezone2tzstring.example.com/?timezone=")) + urlencoded_payload));
  if (retval != 0) {
     return NULL;  // Failure
  }
  return payload.c_str();
}

// End of get_tz_string.ino
