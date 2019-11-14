# tzdata2tzstring
Localtime support in low-memory IoT devices
## Justification

During the last several years, personal computers and smartphones became
capable
of displaying the local time, correctly adjusted for daylight saving time
(DST) - and
without requiring human intervention beyond selecting the correct timezone.

Nowadays, there are also some IoT devices, which need to support
local time management - displaying it, or otherwise making it available.

Timekeeping is performed using the Internet protocol NTP, which provides
the correct UTC. When using a PC or a smartphone, the timezone is
usually selected by manual user action.

However, some IoT devices may not have
the UI needed for convenient timezone selection. Then it is desirable to
support automatic timezone selection as a default.

### How to implement automatic timezone selection?
There are some websites, which discover your IP address and provide you with
the best guess of your timezone.

The following tables lists some of those websites.

Name | Account or API key? | Finds your IP? | Response format
-----|---------------------|----------------|----------------
[timezonedb](https://timezonedb.com/)    | Yes        | Yes      | XML/JSON
[ipapi](https://ipapi.co/)         | No         | Yes      | text
[Timezone API](https://timezoneapi.io/)  | Yes        | Yes      | JSON (including tz_string)
[ipgeolocation](https://ipgeolocation.io/) | Yes        | Yes      | XML/JSON

Since those websites usually provide the timezone name rather than the
string describing the DST transition dates (the so-called `tz_string`),
the next step is to figure out the DST transition dates from
the timezone name.

In devices with plenty of memory this is carried out
by means of a timezone database.

For example, in Debian/Ubuntu based systems, this
database is stored in the `/usr/share/zoneinfo` directory and occupies 3.5MB
(the relevant package in Ubuntu 18.04 is `tzdata` and its version,
as of Nov. 2019, is `2019c-0ubuntu0.18.04`).

### Memory constrained IoT devices
However, IoT devices are typically based upon memory-constrained controllers
and
cannot afford to store locally the whole timezone database - just to
correctly determine the local time for a single timezone.

Therefore, IoT devices need to access an Internet based service to get the
correct timezone information, just as they get UTC time updates using NTP.
In other words, those IoT devices effectively outsource the timezone
database management.

### Internet service for providing the timezone information
An Internet service, for providing the correct `tz_string` corresponding
to a timezone name, needs to keep the timezone database up to date at
all times.

I implemented the internet service as follows.

1. A machine, running an Ubuntu 18.04 installation with a webserver,
is used.
1. The Internet service is implmented as a small WSGI-based website.
1. A script scans the `/usr/share/zoneinfo` contents and creates a small
database for translating timezone names into the corresponding `tz_string`
values.
1. There is a mechanism for invoking the above script and restarting the web server
each time the `tzdata` package is updated/installed/re-installed.

The actual implementation is described in the following section.

## Parts of the project
1. WSGI-based website (the "tzstring website") for mapping from timezone
into tz_string.
1. Database builder
1. Trigger scripts
1. Sample client code

### WSGI-based website
* `wsgi.py` - creates the WSGI application
* `tzstring.py` - stores the `timezone` - `tz_string` translation database
in memory and provides the `tz_string` as a response to queries with the
`timezone` parameter. When a `timezone` is not recognized, `"UTC"` is returned.

A redacted Apache2 configuration file is provided as well
(`tzstring_example_com.conf`).

### Database builder
* `build_tz_string_db.py` - scans the `/usr/share/zoneinfo` contents
and builds from them the database used by `tzstring.py`.

### Trigger scripts
Those trigger scripts cause the database builder script to be executed
and the webserver to be restarted whenever the `tzdata` package is
updated.

* `99zz-tzdata-trigger-postupgrade` configures apt to execute, before
actual upgrade,
`tzdata-trigger-postupgrade.sh` and provide it with a list of packages to be updated.
In addition to the above, apt is configured to execute `tzdata-update-tzstring-db.sh` once all packages have been updated.
* `tzdata-trigger-postupgrade.sh` determines whether `tzdata` is one of the
packages to be updated. If yes, it gets `tzdata-update-tzstring-db.sh` to
actually do its job.
* `tzdata-update-tzstring-db.sh` performs the actual tzstring database
and webserver restart.

### Sample client code
The provided sample client code is an ESP8266 sketch. **See usage instructions below.**

#### What does it do?
##### During the setup phase:
1. The client code performs the usual initializations.
1. Then it tries to connect to WiFi using already-configured SSID and password.
   1. If unsuccessful, it opens an access point whose SSID and password are the
values of `AP_SSID` and `AP_PASSWORD` respectively.
   1. An user can configure SSID and password by connecting to the above
access point and browsing to `http://192.168.4.1/`.
1. Once the client code connects to the user's WiFi access point and has access
to the Internet, it configures the UTC using NTP.
1. Finally, the client code retrieves the `tz_string` for the timezone
in which the system is connected to the Internet.

##### During the loop phase:
1. If more than 24 hours passed since the last NTP update, NTP is queried
and the UTC is updated.
1. If the UTC has changed (it changes once per second), new localtime is
computed from it and written to the Serial port.

The loop phase is repeated 10 times per second.

#### The client code modules
* ESP8266_auto_timezone_demo.ino - is the main module and it operates as
described above.
* get_tz_string.ino - is in charge of fetching the `tz_string` for the
current timezone.

  Example: for the timezone `Asia/Jerusalem`, the tz_string
value is `IST-2IDT,M3.4.4/26,M10.5.0`.
* urlencode.ino - is in charge of URLencoding the timezone before sending it
to the tzstring website.

#### Build environment
The sample client code (before redacting) was compiled on Arduino IDE v1.8.10
with some ESP8266 libraries installed. The board used was NodeMCU v3, and the
IDE was configured to work with board "NodeMCU 1.0 (ESP-12E Module)".

#### DISCLAIMER
The sample client code does not include code for manual overrides of the
timezone determination, entry of custom tz_string, or manual setting of
the local time *vs.* UTC offset.

## Usage instructions
The code, as it is, is not ready for running. You need to edit files
as follows.
* Insert into `get_tz_string.ino` the domain names of the websites you'll actually use for
discovering your timezone (a list of suitable services can be found
in `get_tz_string.h`) and for converting it into tz_string (you need
to register a domain name and set up this website).
* You need also to choose an username instead of `user` and edit all usages
of this username in the files.
* You may want also to change some filenames and the locations of some
scripts and data files.


## DISCLAIMER
* I did not invest time in polishing the project's files.
* When the project is properly polished, it should include also a
cookiecutter type configuration file.
* After redacting the files, they were not tested. However, they are
based upon a working project.
