# -*- coding: utf-8 -*-
#
# wsgi.py - App runner for tzstring website
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
import os
# Third-party imports
import falcon
# Local imports
import tzstring

# Create resources
## Hardwired here because an attempt to SetEnv in Apache2 for
## mod_wsgi did not work.
db_fname = "/home/user/tmp/tzstring-database"
tzstring_resource = tzstring.TZStringResource(db_fname)

# Create falcon app
application = falcon.API()
application.add_route('/tzstring', tzstring_resource)


# Useful for debugging problems in API, it works with pdb
if __name__ == '__main__':
    from wsgiref import simple_server  # NOQA
    httpd = simple_server.make_server('127.0.0.1', 8000, application)
    httpd.serve_forever()

# End of wsgi.py
