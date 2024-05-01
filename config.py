#!/glade/apps/opt/modulefiles/idep python
from __future__ import print_function

from os import getenv, chdir, system
from subprocess import check_output

user_id = getenv('USER')

# The member class is used in a list comprehension
class Member:
    def __init__(self, index, case):
        self.string = str(index).zfill(4)
        self.name = case.name + '_' + self.string
        self.caseroot_path = case.caseroot_path + '/' + self.name
        self.scratchroot_path = case.scratchroot_path + '/'  + self.name
        self.rundir = self.scratchroot_path + '/run'

    def git_init(self):
        chdir(self.caseroot_path)
        system('git init')
        system('git add .')
        system('git commit -m "Initial caseroot commit for ' + self.name + '"')

        chdir(self.scratchroot_path)
        system('git init')
        system('git add .')
        system('git commit -m "Initial runroot commit for ' + self.name + '"')

    def git_commit(self):
        chdir(self.caseroot_path)
        system('git add .')
        system('git commit -m "Caseroot commit for ' + self.name + '"')

        chdir(self.scratchroot_path)
        system('git add .')
        system('git commit -m "Runroot commit for ' + self.name + '"')

    def git_reset(self):
        chdir(self.caseroot_path)
        system('git reset --hard HEAD^')

        chdir(self.scratchroot_path)
        system('git reset --hard HEAD^')

    def check_build_success(self):
        chdir(self.caseroot_path)
        case_status = open(self.caseroot_path + '/CaseStatus', 'r')
        second_to_last_line = case_status.readlines()[-2]

        if 'case.build success' in second_to_last_line:
            build_successful = True
        else:
            build_successful = False

        return build_successful

    def xml_change(self, command):
        chdir(self.caseroot_path)
        system('./xmlchange ' + command)

    def xml_query(self, command):
        chdir(self.caseroot_path)
        system('./xmlquery ' + command)

    def xml_get_value(self, key):
        chdir(self.caseroot_path)
        return check_output('./xmlquery ' + key + ' --value', shell=True).decode('utf-8')

class Experiment:
    """The Experiment class is essentially used as a namelist. Some dictators
    of python style suggest that this type of data should be stored as
    key/value pairs in a dictionary instead of using an object. However we're
    using an object so that the syntax is more uniform throughout the
    scripts."""
    def __init__(self):
        # Case config
        self.name = 'GIAF'
        self.size = 3
        self.compset = 'GIAF'
        self.resolution = 'f09_g17'
        self.compset_args = ' --compset ' + self.compset + ' --run-unsupported '
        self.cesmtag = 'cesm2_1_3'
        self.cesmtagmajor = 'cesm2_1'
        self.start_year = '2018'
        self.start_month = '01'
        self.start_day = '01'
        self.start_tod = '00000'
        self.start_timestamp = self.start_year + '-' + self.start_month + '-' + self.start_day + '-' + self.start_tod
        # Restart timestamp is only used to fix a broken run, so by default it is sent to None
        self.restart_timestamp = None
        self.restart_dir = None
        self.stop_option = 'nhours'
        self.stop_n = '6'
        self.short_term_archiver = 'off'
        self.debug = True
        self.machine = 'derecho'
        self.email_address = 'johnsonb@ucar.edu'
        # Paths
        self.cesmdata_path = '/glade/p/cesmdata/cseg/inputdata'
        self.acom_path = '/gpfs/csfs1/acom'
        self.caseroot_path = '/glade/work/' + user_id + '/cases/' + self.name
        self.scratch_path = '/glade/derecho/scratch'
        self.scratchroot_path = self.scratch_path + '/' + user_id + '/' + self.name
        self.cesmroot_path = '/glade/work/' + user_id + '/' + self.cesmtag
        self.sourcemods_path = '/glade/u/home/' + user_id + '/' + self.cesmtag + '/SourceMods'
        self.dartroot_path = '/glade/work/' + user_id + '/git/DART_derecho'
        self.baseobsdir_path = '/glade/p/cisl/dares/Observations/NCEP+ACARS+GPS+AIRS/Thinned_x9x10'
        self.cimeroot_path = self.cesmroot_path + '/cime'
        self.use_tasks_per_node = 128
        self.nthreads = 1
        self.archdir_path = self.scratch_path + '/' + user_id + '/archive/' + self.name
        self.python_bin = '/glade/u/home/johnsonb/miniconda2/bin/python'
        self.scripts_path = '/glade/work/johnsonb/git/asynchronous_cesm'
        # DATM
        self.stream_year_align = 2011
        self.stream_year_first = 2011
        self.stream_year_last = 2015

        # Reference
        self.ref_case = 'g210.G_JRA.v14.gx1v7.01'
        self.ref_year = '2010'
        self.ref_mon = '01'
        self.ref_day = '01'
        self.ref_tod = '00000'
        self.ref_date = self.ref_year + '-' + self.ref_mon + '-' + self.ref_day
        self.ref_timestamp = self.ref_year + '-' + self.ref_mon + '-' + self.ref_day + '-' + self.ref_tod
        self.ref_stage_dir_path = self.scratch_path + '/' + user_id + '/' + self.ref_case + '/rest/' + self.ref_timestamp
        # Job
        self.project = 'ACIS0001'
        self.queue = 'main'
        self.walltime = '04:00:00'

experiment = Experiment()
# Use a list comprehension for members
members = [Member(index+1, experiment) for index in range(0, experiment.size)]
