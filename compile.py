#!/glade/apps/opt/modulefiles/idep python
from __future__ import print_function

import os
from config import experiment, members
from utils import cron, database

if not os.path.exists(experiment.caseroot_path):
    os.system('mkdir -p ' + experiment.caseroot_path)

# Create a default record in the database for this ensemble

with database as db:
    db.create_tables()

# Declare a job string

# The curly braces allow the user to insert strings using the format method.
# The inserted strings in this job_string correspond to 
# 1. job_name
# 2. project_code
# 3. user_email
# 4. job_command

job_string = """#!/bin/bash -l
#PBS -N {}
#PBS -A {}
#PBS -l walltime=02:00:00
#PBS -q main
#PBS -j oe
#PBS -k eod
#PBS -m abe
#PBS -M {}
#PBS -l select=1:ncpus=36:mpiprocs=36

{}
"""

# Build a single case

for member in members:

    job_name = experiment.name + "_" + member.string
    job_filename = 'job_scripts/' + job_name + '.sh'

    job_command = 'python ./compile_single.py ' + member.string

    f = open(job_filename, "w")
    f.write(job_string.format(job_name, experiment.project, experiment.email_address, job_command))
    f.close()

    run_command = 'qsub ./' + job_filename
    print(run_command)
    os.system(run_command)

# Create a check_database chronjob

cron.create_job()
