#!/glade/apps/opt/modulefiles/idep python
from __future__ import print_function

import unittest
from utils import cron, database, members
from config import experiment
import os
from os.path import isdir, isfile, islink
import time

class TestPaths(unittest.TestCase):
    """
    Test whether the paths, binaries and files in the experiment object exist.
    """

    def test_paths_experiment(self):

        all_paths_and_files_exist = True

        for item in vars(experiment).items():
            if item[0].split('_')[-1] == 'path':
                if not isdir(item[1]):
                    print(item[0] + ' path does not exist: ' + item[1])
                    all_paths_and_files_exist = False
            elif item[0].split('_')[-1] == 'bin':
                if not isfile(item[1]) and not islink(item[1]):
                    print(item[0] + ' binary does not exist: ' + item[1])
                    all_paths_and_files_exist = False
            elif item[0].split('_')[-1] == 'file':
                if not isfile(item[1]) and not islink(item[1]):
                    print(item[0] + ' file does not exist: ' + item[1])
                    all_paths_and_files_exist = False

        self.assertTrue(all_paths_and_files_exist)

class TestGit(unittest.TestCase):
    """
    Test whether git is installed on your system.
    """

    def test_git(self):
        result = os.system('git -v')
        self.assertEqual(result, 0)

class TestCron(unittest.TestCase):
    """
    Test the cron class by creating a new cronjob in the crontab to run the
    ``write_time_to_file.py`` script. Whenever that script is run, it simply
    writes the current time to the text file specified by the ``output_file``
    variable. The cron job is run once a minute and the test is paused for
    a set number of minutes, specified by the ``test_duration_in_minutes``
    variable. If the number of lines in the ``output_file`` matches the number
    of minutes the test has been paused then the test passes.

    If you have already ensured that cron works on your system and are running
    the test suite multiple times and don't want to wait for test_cron to pass
    each time, set ``test_duration_in_minutes = 0`` and the test will pass.
    """

    def test_cron(self):
        test_duration_in_minutes = 1
        seconds_per_minute = 60
        script = 'write_time_to_file.py'
        output_file = experiment.scripts_path + '/times_written_to_file.txt'
        # Create an empty file that can be read even if
        # ``test_duration_in_minutes = 0``.
        open(output_file, 'w').close()

        print('Running test_cron, which will pause test_utils.py for ' + str(test_duration_in_minutes) + ' minute(s).')

        if test_duration_in_minutes != 0:
            # Create a cron job that is run every minute
            cron.create_job(1, script, output_file)

            time.sleep(test_duration_in_minutes*seconds_per_minute)

            cron.cancel_job(script, output_file)

        with open(output_file, mode='r') as file:
            nlines = len(file.readlines())

        os.remove(output_file)
        self.assertEqual(test_duration_in_minutes, nlines)

class TestDatabase(unittest.TestCase):
    """
    Test the database class by creating a test database, inserting records into
    it, selecting a subset of these records, updating the selected records and
    inserting them back into the test database.
    """

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
