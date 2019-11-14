#!/bin/bash
if grep -q /var/cache/apt/archives/tzdata ; then
    touch /tmp/tzdata-was-upgraded
fi
# End of tzdata-trigger-postupgrade.sh
