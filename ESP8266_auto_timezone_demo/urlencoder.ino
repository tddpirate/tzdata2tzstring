///////////////////////////////////////////////////////////////////////////////////
// URL encoder
//
// Encode space as '+'
// Encode non-alphanumeric characters as %xx
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
// Was inspired by: https://www.geekhideout.com/urlcode.shtml which was put under
// public domain: https://creativecommons.org/publicdomain/zero/1.0/
///////////////////////////////////////////////////////////////////////////////////

#include "urlencoder.h"

// Convert an integer value into its hex character equivalent.
const char hex[] PROGMEM = "0123456789abcdef";
char to_hex(char code) {
  return pgm_read_byte(hex + (code & 15));
}

// The caller provides memory for the URLencoded string so that it'll be able to free it when done.
void urlencode(const String& str, String& urlencoded_str)
{
  urlencoded_str.reserve(str.length()*3 + 1);
  for (unsigned int ind = 0; ind < str.length(); ++ind) {
    char curchar = str.charAt(ind);
    if (isalnum(curchar) || curchar == '-' || curchar == '_' || curchar == '.' || curchar == '~') {
      urlencoded_str += curchar;
    }
    else if (curchar == ' ') {
      urlencoded_str += '+';
    }
    else {
      urlencoded_str += '%';
      urlencoded_str += to_hex(curchar >> 4);
      urlencoded_str += to_hex(curchar & 15);
    }
  }
}

// End of urlencoder.ino
