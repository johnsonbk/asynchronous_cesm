#!/glade/apps/opt/modulefiles/idep python
from __future__ import print_function

from utils import database, cron, message
from config import experiment

# Check the status of the experiment
with database as db:
    experiment_record = db.select_experiment_record()

print("experiment_record['status']")
print(experiment_record['status'])

if experiment_record['status'] == 'building':
    with database as db:
        statuses = db.select_all_member_statuses_in_cycle_record(experiment_record['cycle'])

    if all(status == 'completed building' for status in statuses.values()):

        with database as db:
            db.update_status_in_experiment_record(1, 0, 'completed building')

        message_subject = experiment.name + ' completed building'
        message_content = 'View the completed build at ' + experiment.caseroot_path
        message.send(message_subject, message_content)
        cron.cancel_job()
        
    elif any(status == 'failed building' for status in statuses.values()):

        with database as db:
            db.update_status_in_experiment_record(0, 0, 'failed building')

        message_subject = experiment.name + ' failed building'
        message_content = 'View the failed build at ' + experiment.caseroot_path
        message.send(message_subject, message_content)
        cron.cancel_job()

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
