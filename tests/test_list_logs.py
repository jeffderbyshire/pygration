import pprint
from migrate_helper_scripts import list_logs

logs = list_logs.get_logs("errors", volumes=list('VPV008'))
pprint.pprint(logs)