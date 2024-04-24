#!/glade/apps/opt/modulefiles/idep python
from __future__ import print_function

import os
from config import experiment
from utils import cron, database

if not os.path.exists(experiment.root):
    os.system('mkdir -p ' + experiment.root)

# Declare a job string

# The curly braces allow the user to insert strings using the format method.
# The inserted strings in this job_string correspond to 
# 1. job_name
# 2. project_code
# 3. user_email
# 4. load_environment
# 5. job_command

user_email = 'johnsonb@ucar.edu'
load_environment = 'conda activate glade_env'

job_string = """#!/bin/bash -l
#PBS -N {}
#PBS -A {}
#PBS -l walltime=02:00:00
#PBS -q regular
#PBS -j oe
#PBS -k eod
#PBS -m abe
#PBS -M {}
#PBS -l select=1:ncpus=36:mpiprocs=36

{}
{}
"""

# Build a single case

for i in range(0, experiment.size):

    instance = str(i+1).zfill(4)

    job_name = experiment.name + "_" + instance
    job_filename = 'job_scripts/' + job_name + '.sh'

    job_command = 'python ./compile_single.py ' + instance

    f = open(job_filename, "w")
    f.write(job_string.format(job_name, experiment.project, user_email, load_environment, job_command))
    f.close()

    run_command = 'qsub ./' + job_filename
    print(run_command)
    os.system(run_command)

# Now that all the batch jobs have been submitted, create a default record
# in the database for this ensemble

with database as db:
    db.create_timestep_record(0, experiment.start_year, experiment.start_month, experiment.start_day, experiment.start_tod, 'building')

# Create a check_database chronjob

cron.create_check_database_job()
