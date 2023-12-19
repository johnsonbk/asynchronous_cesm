#!/glade/apps/opt/modulefiles/idep python

from datetime import date, timedelta
import f90nml
import os


# To modify a namelist but preserve its comments and formatting, create a
# namelist patch and apply it to a target file using the patch function

start_year = 2010
start_month = 1
start_day = 1

obs_seq_path = '/glade/p/cisl/dares/Observations/WOD13/' # 200701/obs_seq.0Z.20070101
output_path = '/glade/derecho/scratch/johnsonb/obs_seq/'
start_date = date(start_year, start_month, start_day)
timedeltas = [timedelta(days=increment) for increment in range(0, 5)]

while start_date.year != 2017:

    # Get the list of dates in this 5-day window
    list_of_dates = [start_date + this_timedelta for this_timedelta in timedeltas]

    # Write the input files to the text file that will be read by obs_sequence_tool
    with open('./obs_sequence_tool_list.txt', 'w') as f:

        for this_date in list_of_dates:
            line = obs_seq_path + str(this_date.year).zfill(4) + str(this_date.month).zfill(2) + '/obs_seq.0Z.' + str(this_date.year).zfill(4) + str(this_date.month).zfill(2) + str(this_date.day).zfill(2)
            f.write(line + '\n')
            print(line)

    # Edit input.nml to set the output file
    filename_out = output_path + 'obs_seq.0Z.' + str(list_of_dates[0].year).zfill(4) + str(list_of_dates[0].month).zfill(2) + str(list_of_dates[0].day).zfill(2) + '_' + str(list_of_dates[-1].year).zfill(4) + str(list_of_dates[-1].month).zfill(2) + str(list_of_dates[-1].day).zfill(2)
    print('filename_out:', filename_out)

    # Patch input.nml
    patch_nml = {'obs_sequence_tool_nml': {'filename_out': filename_out}}
    f90nml.patch('./input.nml', patch_nml, './temp_input.nml')
    os.rename('./temp_input.nml', './input.nml')

    # Run obs_sequence_tool
    os.system('./obs_sequence_tool')
    
    # Increment to the next start date
    start_date = list_of_dates[-1] + timedelta(days=1)
