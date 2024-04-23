#!/glade/apps/opt/modulefiles/idep python
from __future__ import print_function

import datetime
import sys

current_time = datetime.datetime.now()

output_filename = sys.argv[1]

with open(output_filename, mode='a') as file:
    file.write(str(current_time) + '\n')
