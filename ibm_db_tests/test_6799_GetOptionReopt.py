#
#  Licensed Materials - Property of IBM
#
#  (c) Copyright IBM Corp. 2007-2026
#

from __future__ import print_function
import sys
import unittest
import ibm_db
import config
from testfunctions import IbmDbTestFunctions


class IbmDbTestCase(unittest.TestCase):

    def test_6799_GetOptionReopt(self):
        obj = IbmDbTestFunctions()
        obj.assert_expect(self.run_test_6799)

    def run_test_6799(self):
        conn = ibm_db.connect(config.database, config.user, config.password)

        if conn:
            server = ibm_db.server_info(conn)
            if sys.platform == 'zos' or not server.DBMS_NAME.startswith('DB2/'):
                print("SKIPPED")
                ibm_db.close(conn)
                return

            stmt = ibm_db.prepare(conn, "SELECT 1 FROM SYSIBM.SYSDUMMY1")
            # 3 is SQL_REOPT_ONCE, 4 is SQL_REOPT_ALWAYS
            for value in (3, 4):
                rc = ibm_db.set_option(stmt, {ibm_db.SQL_ATTR_REOPT: value}, 0)
                print("set %d: %s, get: %r" % (value, rc, ibm_db.get_option(stmt, ibm_db.SQL_ATTR_REOPT, 0)))
            ibm_db.close(conn)
        else:
            print("Connection failed.")

#__END__
#__LUW_EXPECTED__
#set 3: True, get: 3
#set 4: True, get: 4
#__ZOS_EXPECTED__
#SKIPPED
#__SYSTEMI_EXPECTED__
#SKIPPED
#__IDS_EXPECTED__
#SKIPPED
