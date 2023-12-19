#!/glade/apps/opt/modulefiles/idep python
from __future__ import print_function

from os import system

# For the database class
import sqlite3

# For the message class
from smtplib import SMTP
from email.mime.text import MIMEText

from config import case, members

def verify_path_exists(path):
    from os.path import isdir

    if not isdir(path):
        raise OSError('Path does not exist: ' + path)

class Cron:
    """
    Contains methods to create and delete cron jobs for the observer.py script.
    """

    def __init__(self, case):
        self.python_path = case.python_path
        self.scripts_path = case.scripts_path

    def create_observer_job(self):
        """
        Writes the observer job to the crontab.
        """
        system('crontab -l > ' + self.scripts_path + '/tmp_chrontab')
        f = open(self.scripts_path + '/tmp_chrontab', 'a')
        f.write('*/5  * * * * ' + self.python_path + ' ' + self.scripts_path + '/observer_test.py ' + case.name + '\n')
        f.close()
        system('crontab ' + self.scripts_path + '/tmp_chrontab')
        system('rm ' + self.scripts_path + '/tmp_chrontab')

    def cancel_observer_job(self):
        """
        Reads the crontab contents in f1 and writes them to f2 as long as the
        line doesn't contain the observer, thus it "cancels" the observer job.
        """
        system('crontab -l > ' + self.scripts_path + '/tmp_chrontab_1')
        f1 = open(self.scripts_path + '/tmp_chrontab_1', 'r')
        f2 = open(self.scripts_path + '/tmp_chrontab_2', 'w')

        lines = f1.readlines()
        for line in lines:
            if 'observer_test.py ' + case.name not in line:
                f2.write(line)

        f1.close()
        f2.close()

        system('crontab ' + self.scripts_path + '/tmp_chrontab_2')

        system('rm ' + self.scripts_path + '/tmp_chrontab_1')
        system('rm ' + self.scripts_path + '/tmp_chrontab_2')

class Database:
    """
    Contains methods to handle the sqlite queries needed to record and
    update the state of the ensemble. The connection attribute is the actual
    connection to the sqlite database. Thus database.connection.close() will
    terminate the connection to the sqlite database.
    """

    def __init__(self, case, members):
        self.name = case.caseroot + '/' + 'sqlite3.db'
        self.size = case.size
        self.members = members
        self.start_year = case.start_year
        self.start_month = case.start_month
        self.start_day = case.start_day
        self.start_tod = case.start_tod
        self.debug = case.debug

    def __enter__(self):
        self.connection = sqlite3.connect(self.name)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        return self
        # self.connection.row_factory = sqlite3.Row
        # return self.conn.cursor()

    def __exit__(self, type, value, traceback):
        self.connection.commit()
        self.connection.close()

    def print_query(self, query):
        # This function prints the queries if debug is True
        if self.debug == True:
            print(query)
        else:
            pass

    def create(self):

        with database as db:

            cursor = db.cursor

            # Create a 'case' table that contains information about the case, including its overall status
            query = 'CREATE TABLE experiment (id INTEGER NOT NULL PRIMARY KEY, cycle INTEGER, size INTEGER, start_year INTEGER, start_month INTEGER, start_day INTEGER, start_tod INTEGER, current_year INTEGER, current_month INTEGER, current_day INTEGER, current_tod INTEGER, resubmit INTEGER, status TEXT )'
            cursor.execute(query)

            # Insert a row in the 'case' table to indicate that it is building
            query = "INSERT INTO experiment (id, cycle, size, start_year, start_month, start_day, start_tod, current_year, current_month, current_day, current_tod, resubmit, status) VALUES (0, 0, " + str(self.size) +  ", " + str(self.start_year) + ", " + str(self.start_month) + ", " + str(self.start_day) + ", " + str(self.start_tod) + ", " + str(self.start_year) + ", " + str(self.start_month) + ", " + str(self.start_day) + ", " + str(self.start_tod) + ", 0, 'building')"
            cursor.execute(query)

            # Create a 'cycles' table that contains the status of each ensemble member at each timestep
            query = 'CREATE TABLE cycles (cycle INTEGER NOT NULL PRIMARY KEY, year INTEGER, month INTEGER, day INTEGER, tod INTEGER'

            for this_member in self.members:
                member_string = ', status_of_' + this_member.string + ' TEXT'
                query += member_string

            query += ')'
            cursor.execute(query)

            self.print_query(query)

            self.connection.commit()
    
    def create_timestep_record(self, cycle, year, month, day, tod, status):
        query = "INSERT INTO cycles (cycle, year, month, day, tod"

        for this_member in self.members:
            query += ", status_of_" + this_member

        query += ") VALUES ("+str(cycle) + ", " + year + ", " + month + ", " + day + ", " + tod

        for this_member in self.members:
            query += ", '" + status + "' "
        
        query += ")"

        self.print_query(query)

        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()
    
        return

    def get_record_by_timestamp(self, year, month, day, tod):

        # This gets the newest record with a given timestamp. In general, each record
        # will have a unique timestamp, except cycles 0 and 1 which should have the same timestamp.
        query = "SELECT * FROM cycles WHERE year = " + year + " AND month = " + month + " AND " + "day = " + day + " AND tod = " + tod + " ORDER BY cycle DESC"
        
        self.print_query(query)

        cursor = self.connection.cursor()
        cursor.execute(query)
        record = cursor.fetchone()

        return record

    def get_cycle_year_month_day_tod_resubmit_status_of_case(self):
        query = "SELECT cycle, current_year, current_month, current_day, current_tod, resubmit, status FROM experiment WHERE id = 0"

        cursor = self.connection.cursor()
        cursor.execute(query)
        record = cursor.fetchone()

        return record[0], record[1], record[2], record[3], record[4], record[5], record[6] 

    def get_status_of_member(self, cycle, member):

        query = "SELECT status_of_" + str(member).zfill(4) + " FROM cycles WHERE cycle = " + str(cycle)
        self.print_query(query)

        cursor = self.connection.cursor()
        cursor.execute(query)
        record = cursor.fetchone()

        return record[0]

    def update_status_of_experiment(self, cycle, resubmit, status):

        query = "UPDATE experiment SET cycle = " + str(cycle) + ", resubmit = " + resubmit + ", status = " + status + " WHERE id = 0"
        
        self.print_query(query)

        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()

        return

    def update_status_of_member(self, cycle, member, status):

        query = "UPDATE cycles SET status_of_" + str(member).zfill(4) + " = '" + status + "' WHERE cycle = " + str(cycle)
        
        self.print_query(query)

        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()

        return

    def get_status_of_members(self, cycle):
        # This method returns a dictionary where the keys are the member string
        # for each member of the ensemble and the values are the status of 
        # that member.

        query = "SELECT "
        for imember, this_member in enumerate(self.members):
            if imember+1 != self.size:
                query += "status_of_" + this_member + ", "
            else:
                query += "status_of_" + this_member + " "
        
        query += " FROM cycles WHERE cycle  = " + str(cycle)
        
        self.print_query(query)

        cursor = self.connection.cursor()
        cursor.execute(query)
        record = cursor.fetchone()

        # Create a dictionary where the keys are the member string and the 
        # values are the statuses of the member
        statuses = {}

        for imember, this_member in enumerate(self.members):
            statuses[this_member] = record[imember]

        return statuses

class Message:
    """
    The message class is initialized with the user's email and merely sends
    messages both to and from the user with a status update from the
    experiment.
    """

    def __init__(self, case):
        self.email_address = case.email_address
    
    def send(self, subject, content):

        msg = MIMEText(content)
        msg['Subject'] = subject
        msg['From'] = self.email_address
        msg['To'] = self.email_address

        # Send the message via our own SMTP server.
        s = SMTP('localhost')
        s.sendmail(self.email_address, [self.email_address], msg.as_string())
        # s.send_message(msg)
        s.quit()

cron = Cron(case)
database = Database(case, members)
message = Message(case)
