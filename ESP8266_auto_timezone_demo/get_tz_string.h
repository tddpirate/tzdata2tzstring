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
//
// First, retrieve timezone from a service [1] which finds your IP and provides you
// with your timezone name.
// Then, using a timezone2tzstring service [2], convert your timezone name into the
// corresponding tz_string value.
//
// [1] Some IP to timezone services:
//
// Name          | Account or | Finds    | Response                   | URL
//               | API key?   | your IP? | format                     |
// ----------------------------------------------------------------------------------------------
// timezonedb    | Yes        | Yes      | XML/JSON                   | https://timezonedb.com/
// ipapi         | No         | Yes      | text                       | https://ipapi.co/
// Timezone API  | Yes        | Yes      | JSON (including tz_string) | https://timezoneapi.io/
// ipgeolocation | Yes        | Yes      | XML/JSON                   | https://ipgeolocation.io/
//
// [2] Setting up a timezone2tzstring service website:
//
// See the files in the server subdirectory.
// Typical URL:
//    https://tzstring.example.com/tzstring?timezone={{timezone}}
///////////////////////////////////////////////////////////////////////////////////
#ifndef GET_TZ_STRING_H
#define GET_TZ_STRING_H

const char *get_tz_string();

#endif /* GET_TZ_STRING_H */
// End of get_tz_string.h
