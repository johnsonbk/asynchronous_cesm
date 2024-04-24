#!/glade/apps/opt/modulefiles/idep python
from __future__ import print_function

from utils import database

# Check the status of the experiment

if experiment_record['status'] == 'building':
    pass
elif experiment_record['status'] == 'failed building':
    pass
elif experiment_record['status'] == 'completed building':
    pass
elif experiment_record['status'] == 'assimilating':
    pass
elif experiment_record['status'] == 'failed assimilating':
    pass
elif experiment_record['status'] == 'completed assimilating':
    pass
elif experiment_record['status'] == 'integrating':
    pass
elif experiment_record['status'] == 'failed integrating':
    pass
elif experiment_record['status'] == 'completed integrating':
    pass
