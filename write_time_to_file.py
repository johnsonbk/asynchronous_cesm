#!/glade/apps/opt/modulefiles/idep python
from __future__ import print_function

import datetime
import sys

# This script is called by test_cron. This script writes the current time to 
# a new line in a text file whenever it is called. test_cron calls the script
# once per minute and if the number of lines written to the file matches the
# test duration.

current_time = datetime.datetime.now()

output_filename = sys.argv[1]

with open(output_filename, mode='a') as file:
    file.write(str(current_time)+'\n')
