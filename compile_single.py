#!/glade/apps/opt/modulefiles/idep python
from __future__ import print_function

import os
import sys
from config import experiment, members
from utils import database, message, path_exists

# ---------------------
# Purpose
# ---------------------
#
# This script is designed to set up, stage, and build a single case of a
# CESM ensemble using an "G" compset, where POP and CICE are active.

imember = int(sys.argv[1])
member = members[imember-1]

# The main_name is a directory that contains the single cases that comprise
# the ensemble.
print('case', experiment.name)
print('member.caseroot_path', member.caseroot_path)

create_newcase_command = experiment.cimeroot_path + '/scripts/create_newcase' + \
    ' --case ' + member.caseroot_path + \
    ' --machine ' + experiment.machine + \
    ' --res ' + experiment.resolution + \
    ' --project ' + experiment.project + \
    ' --queue ' + experiment.queue + \
    ' --walltime ' + experiment.walltime + \
    ' --pecount ' + str(experiment.use_tasks_per_node * experiment.nthreads) + \
    experiment.compset_args

print('create_newcase_command', create_newcase_command)

try:
    os.system(create_newcase_command)
except:
    OSError('Case could not be created.')

# Configure the case

member.xml_change('RUN_TYPE=hybrid')
member.xml_change('RUN_STARTDATE='+experiment.start_year+'-'+experiment.start_month+'-'+experiment.start_day)
member.xml_change('START_TOD='+experiment.start_tod)
member.xml_change('RUN_REFCASE='+experiment.ref_case)
member.xml_change('RUN_REFTOD='+experiment.ref_date)
member.xml_change('GET_REFCASE=FALSE')
member.xml_change('CIME_OUTPUT_ROOT='+experiment.scratchroot_path)
member.xml_change('CONTINUE_RUN=FALSE')
member.xml_change('STOP_OPTION='+experiment.stop_option)
member.xml_change('STOP_N='+experiment.stop_n)
member.xml_change('RESUBMIT=0')

if experiment.short_term_archiver == 'off':
    member.xml_change('DOUT_S=FALSE')
else:
    member.xml_change('DOUT_S=TRUE')

member.xml_change('DOUT_S_ROOT='+experiment.archdir_path)

member.xml_change('DEBUG=FALSE')
member.xml_change('INFO_DBUG=0')

print('experiment.sourcemods', experiment.sourcemods_path)
os.system('ls '+experiment.sourcemods_path)
if path_exists(experiment.sourcemods_path):
    os.system('cp -R ' + experiment.sourcemods_path + '/* ' + member.caseroot_path + '/SourceMods')
else:
    print('No SourceMods for this case.')

member.xml_change('RUN_REFDIR=' + experiment.ref_stage_dir_path)

os.system('cd ' + member.caseroot_path)

try:
    os.system('./case.setup')
except:
    OSError('Case could not be set up.')

#####
#     Modify namelists
#####

print('Modify namelist templates for this member.')

user_datm_streams_txt_CPLHISTForcing_Solar = """<dataSource>
    The CAM6-DART Ensemble Reanalysis (NCAR RDA ds345.0) contains
    DATM forcing files particularly appropriate for CESM experiments.
    https://rda.ucar.edu/datasets/ds345.0

    They are available on spinning disk (compressed) on
    the NCAR supercomputers at:
    /glade/collections/rda/data/ds345.0/cpl_unzipped
</dataSource>
<domainInfo>
    <variableNames>
        time          time
        doma_lon      lon
        doma_lat      lat
        doma_area     area
        doma_mask     mask
    </variableNames>
    <filePath>
        /glade/collections/rda/data/ds345.0/cpl_unzipped/""" + member.string + """
    </filePath>
    <fileNames>
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2011.nc
    </fileNames>
</domainInfo>
<fieldInfo>
    <variableNames>
        a2x3h_Faxa_swndr     swndr
        a2x3h_Faxa_swvdr     swvdr
        a2x3h_Faxa_swndf     swndf
        a2x3h_Faxa_swvdf     swvdf
    </variableNames>
    <filePath>
        /glade/collections/rda/data/ds345.0/cpl_unzipped/""" + member.string + """
    </filePath>
    <fileNames>
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2011.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2012.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2013.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2014.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2015.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2016.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2017.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2018.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2019.nc
    </fileNames>
    <offset>
        -5400
    </offset>
</fieldInfo>"""

f = open(member.caseroot_path+"/user_datm.streams.txt.CPLHISTForcing.Solar", "w")
f.write(user_datm_streams_txt_CPLHISTForcing_Solar)
f.close()

user_datm_streams_txt_CPLHISTForcing_State1hr = """<dataSource>
    The CAM6-DART Ensemble Reanalysis (NCAR RDA ds345.0) contains
    DATM forcing files particularly appropriate for CESM experiments.
    https://rda.ucar.edu/datasets/ds345.0

    They are available on spinning disk (compressed) on
    the NCAR supercomputers at:
    /glade/collections/rda/data/ds345.0/cpl_unzipped
</dataSource>
<domainInfo>
    <variableNames>
        time          time
        doma_lon      lon
        doma_lat      lat
        doma_area     area
        doma_mask     mask
    </variableNames>
    <filePath>
        /glade/collections/rda/data/ds345.0/cpl_unzipped/""" + member.string + """
    </filePath>
    <fileNames>
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x1h.2011.nc
    </fileNames>
</domainInfo>
<fieldInfo>
    <variableNames>
        a2x1h_Sa_u           u
        a2x1h_Sa_v           v
    </variableNames>
    <filePath>
        /glade/collections/rda/data/ds345.0/cpl_unzipped/""" + member.string + """
    </filePath>
    <tInterpAlgo>
        linear
    </tInterpAlgo>
    <fileNames>
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x1h.2011.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x1h.2012.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x1h.2013.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x1h.2014.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x1h.2015.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x1h.2016.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x1h.2017.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x1h.2018.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x1h.2019.nc
    </fileNames>
    <offset>
        -1800
    </offset>
</fieldInfo>"""

f = open(member.caseroot_path+"/user_datm.streams.txt.CPLHISTForcing.State1hr", "w")
f.write(user_datm_streams_txt_CPLHISTForcing_State1hr)
f.close()

user_datm_streams_txt_CPLHISTForcing_State3hr = """<dataSource>
    The CAM6-DART Ensemble Reanalysis (NCAR RDA ds345.0) contains
    DATM forcing files particularly appropriate for CESM experiments.
    https://rda.ucar.edu/datasets/ds345.0

    They are available on spinning disk (compressed) on
    the NCAR supercomputers at:
    /glade/collections/rda/data/ds345.0/cpl_unzipped
</dataSource>
<domainInfo>
    <variableNames>
        time          time
        doma_lon      lon
        doma_lat      lat
        doma_area     area
        doma_mask     mask
    </variableNames>
    <filePath>
        /glade/collections/rda/data/ds345.0/cpl_unzipped/""" + member.string + """
    </filePath>
    <fileNames>
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2011.nc
    </fileNames>
</domainInfo>
<fieldInfo>
    <variableNames>
        a2x3h_Sa_z           z
        a2x3h_Sa_tbot        tbot
        a2x3h_Sa_ptem        ptem
        a2x3h_Sa_shum        shum
        a2x3h_Sa_pbot        pbot
        a2x3h_Faxa_lwdn      lwdn
        a2x3h_Sa_dens        dens
        a2x3h_Sa_pslv        pslv
    </variableNames>
    <filePath>
        /glade/collections/rda/data/ds345.0/cpl_unzipped/""" + member.string + """
    </filePath>
    <tInterpAlgo>
        linear
    </tInterpAlgo>
    <fileNames>
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2011.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2012.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2013.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2014.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2015.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2016.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2017.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2018.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2019.nc
    </fileNames>
    <offset>
        -5400
    </offset>
</fieldInfo>"""

f = open(member.caseroot_path+"/user_datm.streams.txt.CPLHISTForcing.State3hr", "w")
f.write(user_datm_streams_txt_CPLHISTForcing_State3hr)
f.close()

user_datm_streams_txt_CPLHISTForcing_nonSolarFlux = """<dataSource>
    The CAM6-DART Ensemble Reanalysis (NCAR RDA ds345.0) contains
    DATM forcing files particularly appropriate for CESM experiments.
    https://rda.ucar.edu/datasets/ds345.0

    They are available on spinning disk (compressed) on
    the NCAR supercomputers at:
    /glade/collections/rda/data/ds345.0/cpl_unzipped
</dataSource>
<domainInfo>
    <variableNames>
        time          time
        doma_lon      lon
        doma_lat      lat
        doma_area     area
        doma_mask     mask
    </variableNames>
    <filePath>
         /glade/collections/rda/data/ds345.0/cpl_unzipped/""" + member.string + """
    </filePath>
    <fileNames>
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2011.nc
    </fileNames>
</domainInfo>
<fieldInfo>
    <variableNames>
        a2x3h_Faxa_rainc     rainc
        a2x3h_Faxa_rainl     rainl
        a2x3h_Faxa_snowc     snowc
        a2x3h_Faxa_snowl     snowl
        a2x3h_Faxa_lwdn      lwdn
    </variableNames>
    <filePath>
        /glade/collections/rda/data/ds345.0/cpl_unzipped/""" + member.string + """
    </filePath>
    <fileNames>
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2011.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2012.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2013.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2014.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2015.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2016.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2017.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2018.nc
        f.e21.FHIST_BGC.f09_025.CAM6assim.011.cpl_""" + member.string + """.ha2x3h.2019.nc
    </fileNames>
    <offset>
        -5400
    </offset>
</fieldInfo>"""

f = open(member.caseroot_path+"/user_datm.streams.txt.CPLHISTForcing.nonSolarFlux", "w")
f.write(user_datm_streams_txt_CPLHISTForcing_nonSolarFlux)
f.close()

user_nl_datm = """
dtlimit  = 1.5, 1.5
fillalgo = 'nn', 'nn'
fillmask = 'nomask','nomask'
mapalgo  = 'bilinear','bilinear'
mapmask  = 'nomask','nomask'
streams  = 'datm.streams.txt.CPLHISTForcing.nonSolarFlux $stream_year_align $stream_year_first $stream_year_last',
           'datm.streams.txt.CPLHISTForcing.Solar        $stream_year_align $stream_year_first $stream_year_last',
           'datm.streams.txt.CPLHISTForcing.State1hr     $stream_year_align $stream_year_first $stream_year_last',
           'datm.streams.txt.CPLHISTForcing.State3hr     $stream_year_align $stream_year_first $stream_year_last'
taxmode  = 'cycle','cycle'
tintalgo = 'linear','linear'
restfils = 'unset'
restfilm = 'unset'
"""
f = open(member.caseroot_path+"/user_nl_datm", "a")
f.write(user_nl_datm)
f.close()

user_nl_cice = """
ice_ic = '""" + member.rundir + """/""" + experiment.ref_case + """.cice_"""+ member.string + """.r.""" + experiment.ref_timestamp + """.nc'
"""
f = open(member.caseroot_path+"/user_nl_cice", "a")
f.write(user_nl_cice)
f.close()

user_nl_pop = """
init_ts_suboption  = 'data_assim'
"""
f = open(member.caseroot_path+"/user_nl_pop", "a")
f.write(user_nl_pop)
f.close()

# os.system('./preview_namelists')

print('Stage the restarts now that the run directory exists.')

# Note to self: restart_time in the csh script is ref_timestamp

continue_run = member.xml_get_value('CONTINUE_RUN')
archived = member.xml_get_value('DOUT_S')
archive_dir = member.xml_get_value('DOUT_S_ROOT')

os.system('cd ' + member.rundir)

print_string = """
Copying the required CESM files to the run directory to rerun a previous step.
CONTINUE_RUN from env_run.xml is """ + continue_run

if continue_run == 'TRUE':
    print_string += " so files for some later step than the initial one will be restaged.\n"
    print_string += "Date to reset files to is: " + experiment.restart_timestamp
else:
    print_string += " so files for the initial step of this experiment will be restaged.\n"
    print_string += "Date to reset files to is: " + experiment.start_timestamp

print(print_string)

if continue_run == 'TRUE':
    print("Staging restart files for run date/time: " + experiment.restart_timestamp)

    if archived == 'TRUE':

        # Check if the stage directory exists
        if path_exists(experiment.ref_stage_dir_path):
           os.system('cp ' + experiment.ref_stage_dir_path + '/*' + member.string + '* ' + member.rundir)
        else:
            raise OSError('Path does not exist: ' + experiment.ref_stage_dir_path)
    else:

        with open(member.caseroot_path + '/rpointer.atm', 'w') as f:
            f.write(experiment.name + '.datm_' + member.string + '.r.' + experiment.restart_timestamp + '.nc\n')
            f.write(experiment.name + '.datm_' + member.string + '.rs1.' + experiment.restart_timestamp + '.bin\n')

        with open(member.caseroot_path + '/rpointer.rof', 'w') as f:
            f.write(experiment.name + '.drof_' + member.string + '.r.' + experiment.restart_timestamp + '.nc\n')
            f.write(experiment.name + '.drof_' + member.string + '.rs1.' + experiment.restart_timestamp + '.bin\n')

        with open(member.caseroot_path + '/rpointer.ice', 'w') as f:
            f.write(experiment.name + '.cice_' + member.string + '.r.' + experiment.restart_timestamp + '.nc\n')
            f.write(experiment.name + '.drof_' + member.string + '.rs1.' + experiment.restart_timestamp + '.nc\n')

        # The ovf restart is only needed for the low-resolution g17 run
        if 'g17' in experiment.resolution:
            with open(member.caseroot_path + '/rpointer.ocn.ovf', 'w') as f:
                f.write(experiment.name + '.pop_' + member.string + '.ro.' + experiment.restart_timestamp)

        with open(member.caseroot_path + '/rpointer.ocn.restart', 'w') as f:
            f.write(experiment.name + '.pop_' + member.string + '.r.' + experiment.restart_timestamp + '.nc\n')
            f.write('RESTART_FMT=nc')

        if os.path.isfile(member.caseroot_path + '/rpointer.ocn.tavg'):
            with open(member.caseroot + '/rpointer.ocn.tavg', 'w') as f:
                f.write(experiment.name + '.pop_' + member.string + '.rh.' + experiment.restart_timestamp + '.nc')

        if os.path.isfile(member.caseroot_path + '/rpointer.ocn.tavg2'):
            with open(member.caseroot + '/rpointer.ocn.tavg2', 'w') as f:
                f.write(experiment.name + '.pop_' + member.string + '.rh.nday1.' + experiment.restart_timestamp + '.nc')

        with open(member.caseroot_path + '/rpointer.drv', 'w') as f:
            f.write(experiment.name + '.cpl.r.' + experiment.restart_timestamp + '.nc')

    print('All files reset to rerun experiment step for time ' + experiment.restart_timestamp + '.')

# Else CONTINUE_RUN == 'FALSE'
else:

    os.system('rm ' + member.caseroot_path + '/rpointer.atm_????')
    os.system('rm ' + member.caseroot_path + '/rpointer.ice_????')
    os.system('rm ' + member.caseroot_path + '/rpointer.ocn_????.tavg')
    os.system('rm ' + member.caseroot_path + '/rpointer.drv')
    os.system('rm ' + member.caseroot_path + '/rpointer.rof')

    print('Staging initial files for instance ' + member.string)

    # The cice fname must match that in the user_nl_cice file
    cice_filename = experiment.ref_case + '.cice_' + member.string + '.r.' + experiment.start_timestamp + '.nc'
    command = 'ln -s ' + experiment.ref_stage_dir_path + '/' + cice_filename + ' ' + member.rundir + '/' + cice_filename
    print(command)
    os.system(command)
    pop_filename = experiment.ref_case + '.pop_' + member.string + '.r.' + experiment.start_timestamp + '.nc'
    command = 'ln -s ' + experiment.ref_stage_dir_path + '/' + pop_filename + ' ' + member.rundir + '/' + pop_filename
    print(command)
    os.system(command)
    popro_filename = experiment.ref_case + '.pop_' + member.string + '.ro.' + experiment.start_timestamp
    command = 'ln -s ' + experiment.ref_stage_dir_path + '/' + popro_filename + ' ' + member.rundir + '/' + popro_filename
    print(command)
    os.system(command)

    with open(member.rundir + '/rpointer.ocn.ovf', 'w') as f:
        f.write(experiment.name + '.pop_' + member.string + '.ro.' + experiment.start_timestamp)

    with open(member.rundir + '/rpointer.ocn.restart', 'w') as f:
        f.write(experiment.name + '.pop_' + member.string + '.r.' + experiment.start_timestamp + '.nc\n')
        f.write('RESTART_FMT=nc')

    print('All files set to run the FIRST experiment step at time' + experiment.start_timestamp)

# ==============================================================================
#
# To create custom stream files we:'
# 1. Use preview_namelists to obtain the contents of the stream txt files
#    in CaseDocs, and then place a copy of the modified stream txt file in
#    ${CASEROOT} with the string user_ prepended, and
# 2. Copy a template stream txt file from this directory:
#    ${DARTROOT}/models/POP/shell_scripts/${cesmtagmajor}
#     and modify one for each instance.
#
# ==============================================================================

print('To create custom stream files we:')
print('1. Use preview_namelists to obtain the contents of the stream txt files')
print('in CaseDocs, and then place a copy of the modified stream txt file in')
print(member.caseroot_path + ' with the string user_ prepended, and')
print('2. Copy a template stream txt file from this directory:')
print(experiment.dartroot_path + '/models/POP/shell_scripts/' + experiment.cesmtagmajor)
print('and modify one for each instance.')

os.system(member.caseroot_path + '/preview_namelists')

# This gives us a stream txt file for each instance that we can
# modify for our own purpose.

# The way to do it in CSHELL foreach FILE (CaseDocs/*streams*)
files = [f for f in os.listdir('./CaseDocs') if 'streams' in f]

for f in files:
    # BKJ ":t" in the line below is just the tail of the file
    # set FNAME = $FILE:t

    if 'presaero' in f:
        print('Using default prescribed aerosol stream.txt file' + f)
    elif 'diatren' in f:
        print('Using default runoff stream.txt file ' + f)
    elif '.Precip_' in f:
        print('Precipitation in user_datm.streams.txt.CPLHISTForcing.nonSolarFlux - not ' + f)
    else:
        print('Double check that ' + f + ' has been written')

#    switch ( ${FNAME} )
#       case *presaero*:
#          echo "Using default prescribed aerosol stream.txt file ${FNAME}"
#          breaksw
#       case *diatren*:
#          echo "Using default runoff stream.txt file ${FNAME}"
#          breaksw
#       case *\.Precip_*:
#          echo "Precipitation in user_datm.streams.txt.CPLHISTForcing.nonSolarFlux - not ${FNAME}"
#          breaksw
#       default:
#          ${COPY} $FILE user_${FNAME}
#          chmod   644   user_${FNAME}
#          breaksw
#    endsw

# end

# Replace each default stream txt file with one that uses the CAM DATM
# conditions for a default year and modify the instance number.
# The stream files for POP have no leading zeros in the instance number.

# print("\nReplacing each default stream txt file with one that uses CAM DATM\n")
# foreach FNAME (user*streams*)
#    set name_parse = `echo ${FNAME} | sed 's/\_/ /g'`
#    @ instance_index = $#name_parse
#    @ filename_index = $#name_parse - 1
#    set streamname = $name_parse[$filename_index]
#    set   instance = `echo $name_parse[$instance_index] | bc`
#    set   string_instance = `printf %04d ${instance}`

#    if (-e $DARTROOT/models/POP/shell_scripts/$cesmtagmajor/user_$streamname*template) then

#       echo "Copying DART template for ${FNAME} and changing instances."

#       ${COPY} $DARTROOT/models/POP/shell_scripts/$cesmtagmajor/user_$streamname*template ${FNAME}

#       sed s/NINST/${string_instance}/g ${FNAME} >! out.$$
#       ${MOVE} out.$$ ${FNAME}

#    else:
#       print("DIED Looking for a DART stream txt template for " + ${FNAME})
#       print("DIED Looking for a DART stream txt template for " + ${FNAME})


# ==============================================================================
# Building the case.
# ==============================================================================
print("\nSetting up the case.\n")
os.system(member.caseroot_path + '/case.setup')
print("\nBuilding the case.\n")
os.system(member.caseroot_path + '/case.build')

build_successful = member.check_build_success()

member.git_init()
member.git_commit()

with database as db:
    if build_successful:
        db.update_member_status_in_cycle_record(0, member.string, 'completed building')
    else:
        db.update_member_status_in_cycle_record(0, member.string, 'failed building')

# ==============================================================================
# Checking the case.
# ==============================================================================

CESM_instructions = """
-------------------------------------------------------------------------

Checking the case.

1) cd """ + member.rundir + """
   and check the compatibility between the namelists/pointer
   files and the files that were staged.

2) cd """ + member.caseroot_path + """

3) The case is initially configured to do NO ASSIMILATION.
   When you are ready to add data assimilation, configure and execute
   the """ + member.caseroot_path + """/CESM_DART_config.csh script.

4) The very first CESM advance (i.e. CONTINUE_RUN=FALSE)
   STOP_N must be longer than *AT LEAST 2 TIMES* the coupling
   frequency between the atmosphere and ocean.
   If coupling once a day, the first advance MUST be at least 48 hours.
   If coupling 4 times a day, the first advance MUST be at least 12 hours.
   After that, STOP_N can be as short as a single coupling frequency.

5) Verify the contents of env_run.xml and submit the CESM job:
   ./case.submit -M begin,end

6) After the job has run, check to make sure it worked and that
   a: POP is creating netCDF restart files,
   b: the right restart files exist in the run directory,
   c: (if you're running DART) the archive dart/hist directory has the DART output,
   d: everything is working correctly ...

7) To extend the run in $STOP_N "$stop_option" steps,
   change the env_run.xml variables:

   ./xmlchange CONTINUE_RUN=TRUE
   ./xmlchange RESUBMIT=<number_of_cycles_to_run>
   ./xmlchange STOP_N=$STOP_N

   and submit:

   ./case.submit -M begin,end

Check the streams listed in the streams text files.  If more or different
dates need to be added, change the $CASEROOT/user_*files*
and invoke './preview_namelists' so you can check the information in the
""" + member.caseroot_path + """/CaseDocs or
""" + member.rundir + """ directories.

-------------------------------------------------------------------------"""

print(CESM_instructions)

with open(member.caseroot_path + '/CESM_instructions.txt', 'w') as f:
        f.write(CESM_instructions)



















# rundir = member.xml_get_value('RUNDIR')
# print('rundir: ' + rundir)
# continue_run = member.xml_get_value('CONTINUE_RUN')
# comp_rof = member.xml_get_value('COMP_ROF')

# ls_command = 'ls ' + rundir + '/*.r.' + case.ref_timestamp + '.nc'
# print(ls_command)
# os.system(ls_command)

# os.system('cd ' + rundir)

# os.system('ln -f ' + case.ref_stage_dir + '/' + case.ref_case + '.clm2_' + member.string +'.r.' + case.ref_timestamp + '.nc ' + rundir)
# os.system('ln -f ' + case.ref_stage_dir + '/' + case.ref_case + '.cice_' + member.string +'.r.' + case.ref_timestamp + '.nc ' + rundir)
# os.system('ln -f ' + case.ref_stage_dir + '/' + case.ref_case + '.cam_' + member.string +'.i.' + case.ref_timestamp + '.nc ' + rundir + '/cam_initial_' + member + '.nc')

# if comp_rof == 'rtm':
#     os.system('ln -f ' + case.ref_stage_dir + '/' + case.ref_case + '.rtm_'+ member.string +'.r.' + case.ref_timestamp + '.nc ' + rundir)
# elif comp_rof == 'mosart':
#     os.system('ln -f ' + case.ref_stage_dir + '/' + case.ref_case + '.mosart_'+ member.string +'.r.' + case.ref_timestamp + '.nc ' + rundir)

# os.system('cd '+ member.caseroot_path)
# os.system('./case.build --skip-provenance-check')

# # Check the case status
# build_successful = member.check_build_success()

# # Initialize the caseroot and scratchroot directories and commit them
# member.git_init()
# member.git_commit()

# if build_successful:
#     database.update_status_of_member(0, member.string, 'build completed')

# else:
#     database.update_status_of_member(0, member.string, 'build failed')

# database.connection.close()
