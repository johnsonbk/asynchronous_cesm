#!/glade/apps/opt/modulefiles/idep python
from __future__ import print_function

from os import system

# For the database class
import sqlite3

# For the message class
from smtplib import SMTP
from email.mime.text import MIMEText

from config import experiment, members

def verify_path_exists(path):
    from os.path import isdir

    if not isdir(path):
        raise OSError('Path does not exist: ' + path)

class Cron:
    """
    Contains methods to create and delete cron jobs for the check_database.py script.
    """

    def __init__(self, experiment):
        self.python_path = experiment.python_path
        self.scripts_path = experiment.scripts_path

    def create_job(self, minutes='5', script='check_database.py', experiment=experiment.name):
        """
        Given the minutes, script name and experiment, writes a job to the
        crontab.
        """
        system('crontab -l > ' + self.scripts_path + '/tmp_chrontab')
        f = open(self.scripts_path + '/tmp_chrontab', 'a')
        f.write('*/' + str(minutes) + ' * * * * ' + self.python_path + ' ' + self.scripts_path + '/' + script + ' ' + experiment + '\n')
        f.close()
        system('crontab ' + self.scripts_path + '/tmp_chrontab')
        system('rm ' + self.scripts_path + '/tmp_chrontab')

    def cancel_job(self, script='check_database.py', experiment=experiment.name):
        """
        Reads the crontab contents in f1 and writes them to f2 unless the line
        contains the script and experiment strings. If the line does contain 
        these strings, they are not written to f2, which cancels that
        particular job.
        """
        system('crontab -l > ' + self.scripts_path + '/tmp_chrontab_1')
        f1 = open(self.scripts_path + '/tmp_chrontab_1', 'r')
        f2 = open(self.scripts_path + '/tmp_chrontab_2', 'w')

        lines = f1.readlines()
        for line in lines:
            if script + ' ' + experiment not in line:
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

    def __init__(self, experiment, members):
        self.name = experiment.caseroot + '/' + 'sqlite3.db'
        self.size = experiment.size
        self.members = members
        self.start_year = experiment.start_year
        self.start_month = experiment.start_month
        self.start_day = experiment.start_day
        self.start_tod = experiment.start_tod
        self.debug = experiment.debug

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

    def create_tables(self):

        # Create a 'experiment' table that contains information about the experiment, including its overall status
        query = 'CREATE TABLE experiment (id INTEGER NOT NULL PRIMARY KEY, cycle INTEGER, size INTEGER, start_year INTEGER, start_month INTEGER, start_day INTEGER, start_tod INTEGER, current_year INTEGER, current_month INTEGER, current_day INTEGER, current_tod INTEGER, resubmit INTEGER, status TEXT )'
        self.cursor.execute(query)

        # Insert a row in the 'experiment' table to indicate that it is building
        query = "INSERT INTO experiment (id, cycle, size, start_year, start_month, start_day, start_tod, current_year, current_month, current_day, current_tod, resubmit, status) VALUES (0, 0, " + str(self.size) +  ", " + str(self.start_year) + ", " + str(self.start_month) + ", " + str(self.start_day) + ", " + str(self.start_tod) + ", " + str(self.start_year) + ", " + str(self.start_month) + ", " + str(self.start_day) + ", " + str(self.start_tod) + ", 0, 'building')"
        self.cursor.execute(query)

        # Create a 'cycles' table that contains the status of each ensemble member at each timestep
        query = 'CREATE TABLE cycles (cycle INTEGER NOT NULL PRIMARY KEY, year INTEGER, month INTEGER, day INTEGER, tod INTEGER'

        for this_member in self.members:
            print('this_member.string', this_member.string)
            member_string = ', status_of_' + this_member.string + ' TEXT'
            query += member_string

        query += ')'
        self.cursor.execute(query)

        self.connection.commit()
    
    def insert_cycle_record(self, cycle, year, month, day, tod, status):
        query = "INSERT INTO cycles (cycle, year, month, day, tod"

        for this_member in self.members:
            query += ", status_of_" + this_member.string

        query += ") VALUES ("+str(cycle) + ", " + str(year) + ", " + str(month) + ", " + str(day) + ", " + str(tod)

        for this_member in self.members:
            query += ", '" + status + "' "
        
        query += ")"

        self.print_query(query)

        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()
    
        return

    def select_cycle_record_by_timestamp(self, year, month, day, tod):

        # This gets the newest record with a given timestamp. In general, each record
        # will have a unique timestamp, except cycles 0 and 1 which should have the same timestamp.
        query = "SELECT * FROM cycles WHERE year = " + str(year) + " AND month = " + str(month) + " AND " + "day = " + str(day) + " AND tod = " + str(tod) + " ORDER BY cycle DESC"
        
        self.print_query(query)

        cursor = self.connection.cursor()
        cursor.execute(query)
        record = cursor.fetchone()

        return record

    def select_member_status_in_cycle_record(self, cycle, member):

        query = "SELECT status_of_" + str(member).zfill(4) + " FROM cycles WHERE cycle = " + str(cycle)
        self.print_query(query)

        cursor = self.connection.cursor()
        cursor.execute(query)
        record = cursor.fetchone()

        return record[0]

    def select_experiment_record(self):

        query = "SELECT * from experiment WHERE id = 0"

        cursor = self.connection.cursor()
        cursor.execute(query)
        record = cursor.fetchone()

        return record

    def update_status_in_experiment_record(self, cycle, resubmit, status):

        query = "UPDATE experiment SET cycle = " + str(cycle) + ", resubmit = " + str(resubmit) + ", status = '" + status + "' WHERE id = 0"
        
        self.print_query(query)

        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()

        return

    def update_member_status_in_cycle_record(self, cycle, member, status):

        query = "UPDATE cycles SET status_of_" + member + " = '" +status + "' WHERE cycle = " + str(cycle)
        
        self.print_query(query)

        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()

        return

    def select_all_member_statuses_in_cycle_record(self, cycle):
        # This method returns a dictionary where the keys are the member string
        # for each member of the ensemble and the values are the status of 
        # that member.

        query = "SELECT "
        for imember, this_member in enumerate(self.members):
            if imember+1 != self.size:
                query += "status_of_" + this_member.string + ", "
            else:
                query += "status_of_" + this_member.string + " "
        
        query += " FROM cycles WHERE cycle  = " + str(cycle)
        
        self.print_query(query)

        cursor = self.connection.cursor()
        cursor.execute(query)
        record = cursor.fetchone()

        # Create a dictionary where the keys are the member string and the 
        # values are the statuses of the member
        statuses = {}

        for imember, this_member in enumerate(self.members):
            statuses["status_of_"+this_member.string] = record[imember]

        return statuses

class Message:
    """
    The message class is initialized with the user's email and merely sends
    messages both to and from the user with a status update from the
    experiment.
    """

    def __init__(self, experiment):
        self.email_address = experiment.email_address
    
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

cron = Cron(experiment)
database = Database(experiment, members)
message = Message(experiment)
