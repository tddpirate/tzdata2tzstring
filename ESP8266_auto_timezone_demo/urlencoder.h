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
#ifndef URLENCODER_H
#define URLENCODER_H

// The caller provides memory for the URLencoded string so that it'll be able to free it when done.
void urlencode(const String& str, String& urlencoded_str);

#endif /* URLENCODER_H */
// End of urlencoder.h
