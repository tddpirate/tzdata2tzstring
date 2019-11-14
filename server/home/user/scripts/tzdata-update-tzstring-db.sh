#!/bin/bash
if [ -e /tmp/tzdata-was-upgraded ] ; then
    rm /tmp/tzdata-was-upgraded
    sudo -u user /home/user/scripts/build_tz_string_db.py > /home/user/tmp/tzstring-database
    systemctl restart apache2.service
fi
