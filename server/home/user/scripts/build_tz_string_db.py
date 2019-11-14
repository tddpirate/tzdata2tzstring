#!/usr/bin/env python3
# build_tz_string_db.py
#
# Build a small database for translating from timezone names into
# tz_string definitions.
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
#
# Traverse directory tree (typically in /usr/share/zoneinfo),
# identify binary timezone files, and extract from them the
# current tz_string.
#
# The output is a text file relating timezone filename to tz_string.
#
# Development python environment:
#   pyenv install 3.6.8 # one time only
#   pyenv local 3.6.8
#   pyenv virtualenv venv-tzdata2tzstring  # one time only
#   pyenv activate venv-tzdata2tzstring
#
# Requirements (to be installed using pip install -r requirements.txt:
#   python-magic
#
########################################################################
# Imports
########################################################################

import argparse
import magic
import os
import struct
import sys

import pprint

########################################################################
# Auxiliary functions
########################################################################

class error(Exception):
    pass

########################################################################
# Actual work functions
########################################################################

def eat_44byte_header(buf):
    """Unpack 44-byte header of tzfile.
       The return value is a 9-tuple.
    """
    result = struct.unpack(">4s 1s 15s 6I", buf[:44])
    return result

def validate_44byte_header(version, unpacked, fname):
    """Validate the result of eat_44byte_header.
       version is typically set([b'2', b'3']).
       Throw an exception if invalid.
    """
    if (unpacked[1] not in version):
        raise error("bad version in header", unpacked[1], fname)
    if (tuple(unpacked[0:3:2]) != (b'TZif', 15*b'\x00')):
        raise error("invalid header", fname)

def skip_fields_length(unpacked_header, timelength=4):
    """Skip fields following the first header.
       timelength is either 4 or 8.
    """
    (tzh_ttisgmtcnt, tzh_ttisstdcnt, tzh_leapcnt, tzh_timecnt, tzh_typecnt, tzh_charcnt) = unpacked_header[3:]
    skip_length = timelength*tzh_timecnt + tzh_timecnt + 6*tzh_typecnt + tzh_charcnt + (timelength + 4)*tzh_leapcnt + tzh_ttisstdcnt + tzh_ttisgmtcnt
    # charcnt was omitted by man tzfile. Documented in https://tools.ietf.org/html/rfc8536 section 3.2. TZif Data Block.
    # See also bug report:
    #   https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=944388
    return skip_length

########################################################################
# Test code
########################################################################

def check_dependencies(module_names=["argparse","magic","sys"]):
    """Try to import modules, whose names are given in the argument
       list.
       If all import properly, return [].
       Otherwise, return a list of modules whose import failed, together
       with failure reason.
    """
    failed = []
    for mname in module_names:
        try:
            __import__(mname)
        except Exception as e:
            failed.append((mname,e))
    return(failed)

########################################################################

class TestNumbering:
    """Keep track of current test number, and count of pass/fail in the current group of tests"""
    def __init__(self):
        self.testnum = 0
        self.passed = 0
        self.failed = 0
    def __str__(self):
        return "# Ran {} tests: {} passed, {} failed".format(self.testnum,self.passed,self.failed)
    def next(self):
        """The tests are numbered starting from 1 and ending at N if there are N tests."""
        testno = self.testnum
        self.testnum += 1
        return testno
    def post(self,passed):
        """Post the results of a test.
           If passed is True, increment self.passed.
           Otherwise increment self.failed
        """
        if (passed):
            self.passed += 1
        else:
            self.failed += 1
        assert (self.testnum == (self.passed + self.failed)), "Inconsistency: {} tests, {} passed, {} failed".format(self.testnum,self.passed,self.failed)

########################################################################

def increment_testnum(testnum):
    """Auto-increment test number if it is an instance of TestNumbering.
       The return value is the test number.
    """
    if (isinstance(testnum,TestNumbering)):
        return testnum.next()
    else:
        return testnum

def run_test(testnum,desc,exp,actlambda,stdout=sys.stdout):
    """Boilerplate TAP-compatible test runner.
       testnum - test number, autoincremented if is a list (and hence modifiable).
       desc - test description
       exp - expected value
       actlambda - actual value (written in the form of a parameterless lambda function returning the real actual value if invoked)
       stdout - write a test report

       Return value: True if the test passed, False if the test failed or threw an exception.
    """
    import pprint
    testno = increment_testnum(testnum)

    diagstr = ""
    actval = None
    test_result = False
    try:
        actval = actlambda()
    except Exception as ex:
        stdout.write("not ")
        diagstr = "# exp: %s\n# exception: %s\n" % (pprint.pformat(exp).replace("\n","\n## "),pprint.pformat(ex).replace("\n","\n## "))
    else:
        test_result = (exp == actval)
        if (not test_result):
            stdout.write("not ")
            diagstr = "# exp: %s\n# act: %s\n" % (pprint.pformat(exp).replace("\n","\n## "),pprint.pformat(actval).replace("\n","\n## "))
    stdout.write("ok %d %s\n" % (testno,desc))
    stdout.write(diagstr)
    return test_result   # The caller is responsible for performing testnum.post(), if any.

def run_test_throwing_exception(testnum,desc,expexception,actlambda,stdout=sys.stdout):
    """Same as run_test() above, except that we expect the tested code
       to raise an exception.
       expexception - the expected exception.
           If its class is 'type', then we check only the exception class.
           If its class is a subclass of Exception, then we verify that we got the exact exception we wanted. (NOT IMPLEMENTED)
       other arguments - same as for run_test() above.

       Return value: True if the test threw the expected exception, False otherwise.
    """
    import pprint
    testno = increment_testnum(testnum)

    diagstr = ""
    actval = None
    test_result = False
    try:
        actval = actlambda()
    except Exception as ex:
        if (expexception.__class__ == type):
            test_result = (ex.__class__ == expexception)
        else:
            #test_result = (ex == expexception)
            test_result = (ex.__class__ == expexception.__class__) # As a rule, subclasses of Exception do not have an usable __eq__() implementation.
        if (not test_result):
            diagstr = "# exp: %s\n# act: %s\n" % (pprint.pformat(expexception).replace("\n","\n## "),pprint.pformat(ex).replace("\n","\n## "))
    else:
        # No exception occurred.
        stdout.write("not ")
        diagstr = "# exp: %s\n# act: (no exception was thrown)\n" % pprint.pformat(expexception).replace("\n","\n## ")
    stdout.write("ok %d %s\n" % (testno,desc))
    stdout.write(diagstr)
    return test_result

########################################################################

def run_self_tests(args,stdin=sys.stdin,stdout=sys.stdout,stderr=sys.stderr):
    testnum = TestNumbering()
    # Meta-tests (testing the test functions themselves)
    testnum.post(run_test(testnum,"Meta-test (should pass)",4,(lambda: 2+2),stdout=stdout))
    testnum.post(not run_test(testnum,"Meta-test (should fail)",1,(lambda: 0),stdout=stdout))
    testnum.post(not run_test(testnum,"Meta-test (should fail): due to an exception",2213,(lambda: 1/0),stdout=stdout))
    testnum.post(run_test_throwing_exception(testnum,"Meta-test (should pass): by raising the correct exception",ZeroDivisionError,(lambda: 1/0),stdout=stdout))
    testnum.post(not run_test_throwing_exception(testnum,"Meta-test (should fail): by raising the wrong exception",OverflowError,(lambda: 1/0),stdout=stdout))

    # Standard tests for py3filter.py derived code
    testnum.post(run_test(testnum,"Check dependencies",[],check_dependencies,stdout=stdout))

    # Actual tests
    # None, for now.
    stdout.write("# Summary: {}\n".format(str(testnum)))
    return (testnum.failed == 0)

########################################################################
# Main Program
########################################################################

def main(stdout,stderr,args):
    for dirpath, dirnames, files in os.walk(args.directory, followlinks=True):
        for file_name in files:
            fn_full = os.path.join(dirpath, file_name)
            fn = os.path.relpath(fn_full, args.directory)
            with open(fn_full, 'rb') as file:
                buf = file.read()
                # magic.from_file() did not go into symbolic links' contents.
                mimetype = magic.from_buffer(buf, mime=True)
                description = magic.from_buffer(buf)
                if (mimetype != "application/octet-stream"):
                    stderr.write(f"{fn}: bad MIME type {mimetype}\n")
                    continue
                if (description.startswith("timezone data, version 2") or description.startswith("timezone data, version 3")):
                    data = eat_44byte_header(buf)
                    validate_44byte_header(set([b'2',b'3']), data, fn)
                    skip_length = skip_fields_length(data, timelength=4)
                    data2 = eat_44byte_header(buf[44 + skip_length:])
                    validate_44byte_header(set([data[1]]), data2, fn) # Both headers need to declare the same version.
                    skip2_length = skip_fields_length(data2, timelength=8)
                    total_skip_length = 44 + skip_length + 44 + skip2_length
                    if (args.verbose > 0):
                        stderr.write(f"\n\n{fn}: version {data[1].decode()}\n")
                        stderr.write(f"  First header: {pprint.pformat(data)}\n")
                        stderr.write(f"  Second header: {pprint.pformat(data2)}\n")
                        stderr.write(f"  Skip lengths: first {skip_length}; second {skip2_length}\n")
                        stderr.write(f"total skip: {total_skip_length:04x}; enclosure1: {buf[total_skip_length]}; enclosure2: {buf[-1]}\n")

                    if ((buf[total_skip_length] != b'\n'[0]) or (buf[-1] != b'\n'[0])):
                        raise error("invalid enclosure of tz_string", buf[total_skip_length:])
                    stdout.write(f"{fn}\t{buf[total_skip_length+1:-1].decode()}\n")
                elif (description.startswith("timezone data, version")):
                    raise error("unsupported tzfile version", description, fn)
                else:
                    raise error("unknown tzfile version", description, fn)


########################################################################

if (__name__ == '__main__'):
    parser = argparse.ArgumentParser(
        description="Build timezone to tz_string database",
        epilog="")

    parser.add_argument("-o","--output",
                        type=argparse.FileType('w', encoding='UTF-8'),
                        dest="output",
                        default=sys.stdout,
                        help="Name of output file holding the database.  Default is sys.stdout.")
    parser.add_argument("-e","--error",
                        type=argparse.FileType('w', encoding='UTF-8'),
                        dest="error",
                        default=sys.stderr,
                        help="Name of error output file.  Default is sys.stderr.")
    parser.add_argument("-d","--directory",
                        dest="directory",
                        default="/usr/share/zoneinfo",
                        help="Directory having the binary timezone files, default is {default}")

    parser.add_argument("-t","--test",action="store_true",
                        dest="test",
                        help="Run self tests.")
    parser.add_argument("-v","--verbose",action="count",default=0,
                        dest="verbose",
                        help="Increase output verbosity.")

    args = parser.parse_args()


    # Did we want to run self tests?

    if (args.test):
        sys.exit(0 if run_self_tests(args,stdout=args.output,stderr=args.error) else 1)

    ####################################################################
    # ACTUAL WORK
    ####################################################################
    sys.exit(main(stdout=args.output,stderr=args.error,args=args))

else:
    # I have been imported as a module.
    pass

########################################################################
# End of build_tz_string_db.py
