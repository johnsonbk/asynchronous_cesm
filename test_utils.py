#!/glade/apps/opt/modulefiles/idep python
from __future__ import print_function

import unittest
from utils import cron, database, members
import os

class TestCron(unittest.TestCase):
    pass

class TestDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        database.name = 'test_sqlite3.db'

        with database as db:
            print('Creating database saved in ' + database.name)
            db.create_tables()

    @classmethod
    def tearDownClass(cls):
        print('Removing database saved in ' + database.name)
        os.remove(database.name)

        
    def test_database(self):

        with database as db:
            query = "SELECT name FROM sqlite_master WHERE TYPE='table'"
            db.cursor.execute(query)
            result = db.cursor.fetchall()

            self.assertEqual(len(result), 2)

            print(len(result))

            cycle = 1
            year = 2023
            month = 3
            day = 19
            tod = 38640
            status = 'building'

            db.insert_cycle_record(cycle, year, month, day, tod, status)

            record = db.select_cycle_record_by_timestamp(year, month, day, tod)

            self.assertEqual(record['cycle'], cycle)
            self.assertEqual(record['year'], year)
            self.assertEqual(record['month'], month)
            self.assertEqual(record['day'], day)
            self.assertEqual(record['tod'], tod)
            self.assertEqual(record['status_of_'+members[0].string], status)

            statuses = db.select_all_member_statuses_in_cycle_record(cycle)
            print('statuses', statuses)
            for imember, this_member in enumerate(members):
                self.assertEqual(statuses['status_of_'+this_member.string], 'building')

            new_status = 'completed building'

            db.update_member_status_in_cycle_record(cycle, members[0].string, new_status)
            record = db.select_cycle_record_by_timestamp(year, month, day, tod)

            returned_status = db.select_member_status_in_cycle_record(cycle, members[0].string)

            self.assertEqual(returned_status, new_status)
 
            record = db.select_experiment_record()
            self.assertEqual(record['cycle'], 0)

            resubmit = 10
            experiment_status = 'completed building'

            db.update_status_in_experiment_record(cycle, resubmit, experiment_status)
            record = db.select_experiment_record()
            self.assertEqual(record['status'], experiment_status)
    
if __name__ == '__main__':
    unittest.main()

#setUp()
    
#tearDown()
    
#setUpClass()
    
#tearDownClass()

# assertEqual(a, b)
# assertNotEqual(a, b)
# assertTrue(x)
# assertFalse(x)
# assertIs(a, b)
# assertIsNot(a, b)
# assertIsNone(x)
# assertIsNotNone(x)
# assertIn(a, b)
# assertNotIn(a, b)
# assertIsInstance(a, b)
# assertNotIsInstance(a, b)
