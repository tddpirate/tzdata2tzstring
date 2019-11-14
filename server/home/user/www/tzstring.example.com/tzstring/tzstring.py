# -*- coding: utf-8 -*-
# tzstring.py
#
# This file is part of a small website for providing the service of
# converting timezone names into tz_string definitions.
#
# Copyright (C)2019  Omer ZAK
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
########################################################################

# System imports
import json
from urllib.parse import parse_qs
# Third-party imports
import falcon
# Local imports

class TZStringResource(object):
    """ Service requests to translate timezone into tz_string.
    """
    def __init__(self, db_fname):
        self.tz_db = {}
        with open(db_fname) as db_file:
            for line in db_file:
                (timezone,tz_string) = line[:-1].split(sep='\t')
                self.tz_db[timezone] = tz_string

    def on_get(self, req, resp):
        print(f"request: query={req.query_string} caller={req.access_route}")
        query = parse_qs(req.query_string)
        if ('timezone' not in query):
            resp.status = falcon.HTTP_400
            resp.body = 'UTC'
        elif (len(query['timezone']) != 1):
            resp.status = falcon.HTTP_400
            resp.body = 'UTC'
        elif (query['timezone'][0] not in self.tz_db):
            resp.status = falcon.HTTP_404
            resp.body = 'UTC'
        else:
            resp.status = falcon.HTTP_200
            resp.body = self.tz_db[query['timezone'][0]]

# End of tzstring.py
