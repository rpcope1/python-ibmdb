#
#  Licensed Materials - Property of IBM
#
#  (c) Copyright IBM Corp. 2007-2026
#

from __future__ import print_function
import os
import tempfile
import unittest
import ibm_db
import config
from testfunctions import IbmDbTestFunctions


class IbmDbTestCase(unittest.TestCase):

    def test_6798_DebugLogText(self):
        obj = IbmDbTestFunctions()
        obj.assert_expect(self.run_test_6798)

    def debug_log(self, func):
        fd, log = tempfile.mkstemp(suffix=".log")
        os.close(fd)
        try:
            ibm_db.debug(log)
            try:
                func()
            except Exception:
                pass
            finally:
                ibm_db.debug(False)
            with open(log, "rb") as f:
                return f.read()
        finally:
            os.remove(log)

    def print_valid(self, data):
        try:
            data.decode("utf-8")
            print("log is valid UTF-8: True")
        except UnicodeDecodeError:
            print("log is valid UTF-8: False")

    def run_test_6798(self):
        conn = ibm_db.connect(config.database, config.user, config.password)

        if conn:
            # SQLWCHAR text was formatted with %ls, which reads 4-byte wchar_t
            # where the buffer holds 2-byte SQLWCHAR. Odd and even lengths.
            for sql in ("SELECT 1 FROM SYSIBM.SYSDUMMY1", "SELECT 12 FROM SYSIBM.SYSDUMMY1"):
                data = self.debug_log(lambda: ibm_db.prepare(conn, sql))
                self.print_valid(data)
                lines = [l for l in data.decode("utf-8", "replace").splitlines()
                         if "Preparing SQL statement" in l]
                print("prepare log line ok: %s" % (lines == ["[DEBUG] - Preparing SQL statement, size: %d" % len(sql)]))
                print("statement logged: %s" % (("[DEBUG] - Initial py_stmt: %s" % sql) in data.decode("utf-8", "replace")))

            # createdb()/dropdb() log their arguments before calling the driver.
            # The name is too long to be valid, so the driver rejects it.
            server = ibm_db.server_info(conn)
            if server.DBMS_NAME.startswith('DB2/'):
                name = "NX_6798_TOO_LONG"
                data = self.debug_log(lambda: ibm_db.createdb(conn, name, "UTF-8", "INTERACTIVE"))
                self.print_valid(data)
                text = data.decode("utf-8", "replace")
                for arg in ("dbName=%s," % name, "codeset=UTF-8,", "mode=INTERACTIVE,"):
                    print("createdb logged %s %s" % (arg, arg in text))
                data = self.debug_log(lambda: ibm_db.dropdb(conn, name))
                self.print_valid(data)
                print("dropdb logged dbName: %s" % (("dbName=%s," % name) in data.decode("utf-8", "replace")))
            ibm_db.close(conn)
        else:
            print("Connection failed.")

#__END__
#__LUW_EXPECTED__
#log is valid UTF-8: True
#prepare log line ok: True
#statement logged: True
#log is valid UTF-8: True
#prepare log line ok: True
#statement logged: True
#log is valid UTF-8: True
#createdb logged dbName=NX_6798_TOO_LONG, True
#createdb logged codeset=UTF-8, True
#createdb logged mode=INTERACTIVE, True
#log is valid UTF-8: True
#dropdb logged dbName: True
#__ZOS_EXPECTED__
#log is valid UTF-8: True
#prepare log line ok: True
#statement logged: True
#log is valid UTF-8: True
#prepare log line ok: True
#statement logged: True
#__SYSTEMI_EXPECTED__
#log is valid UTF-8: True
#prepare log line ok: True
#statement logged: True
#log is valid UTF-8: True
#prepare log line ok: True
#statement logged: True
#__IDS_EXPECTED__
#log is valid UTF-8: True
#prepare log line ok: True
#statement logged: True
#log is valid UTF-8: True
#prepare log line ok: True
#statement logged: True
