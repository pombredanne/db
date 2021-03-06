import unittest
from ZODB.config import databaseFromString

from .base import DBSetup

class DBConfigTest(DBSetup, unittest.TestCase):

    def test_must_have_relstorage(self):
        with self.assertRaisesRegexp(AssertionError, "Invalid storage"):
            databaseFromString("""\
                %import newt.db

                <newtdb foo>
                  <zodb>
                  <mappingstorage>
                  </mappingstorage>
                  </zodb>
                </newtdb>
            """)

    def test_just_relstorage(self):
        db = databaseFromString("""\
            %%import newt.db

            <newtdb foo>
              <zodb>
                <relstorage>
                  <postgresql>
                    dsn dbname=%s
                  </postgresql>
                </relstorage>
              </zodb>
            </newtdb>
            """ % self.dbname)

        from .._db import NewtDB
        self.assertEqual(db.__class__, NewtDB)
        from relstorage.storage import RelStorage
        self.assertEqual(db.storage.__class__, RelStorage)
        from relstorage.adapters.postgresql import PostgreSQLAdapter
        self.assertEqual(db.storage._adapter.__class__, PostgreSQLAdapter)

        db.close()

    def test_newt(self):
        db = databaseFromString("""\
            %%import newt.db

            <newtdb foo>
              <zodb>
                <relstorage>
                  <newt>
                    <postgresql>
                      dsn dbname=%s
                    </postgresql>
                  </newt>
                </relstorage>
              </zodb>
            </newtdb>
            """ % self.dbname)

        from .._db import NewtDB
        self.assertEqual(db.__class__, NewtDB)
        from relstorage.storage import RelStorage
        self.assertEqual(db.storage.__class__, RelStorage)
        from .._adapter import Adapter
        self.assertEqual(db.storage._adapter.__class__, Adapter)

        db.close()

    def test_aux(self):
        from newt.db import pg_connection
        conn = pg_connection(self.dsn)
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("create table extra (zoid bigint)")
                cursor.execute("create table extra2 (zoid bigint)")
        conn.close()

        db = databaseFromString("""\
            %%import newt.db

            <newtdb foo>
              <zodb>
                <relstorage>
                  <newt>
                    auxiliary-tables extra extra2
                    <postgresql>
                      dsn dbname=%s
                    </postgresql>
                  </newt>
                </relstorage>
              </zodb>
            </newtdb>
            """ % self.dbname)

        from .._db import NewtDB
        self.assertEqual(db.__class__, NewtDB)
        from relstorage.storage import RelStorage
        self.assertEqual(db.storage.__class__, RelStorage)
        from .._adapter import Adapter
        self.assertEqual(db.storage._adapter.__class__, Adapter)
        self.assertEqual(db.storage._adapter.mover.auxiliary_tables,
                         ['extra', 'extra2'])

        db.close()

