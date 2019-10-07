import sys
from migrate_helper_scripts import migrationLogs

sys.path.append('/home/users/jeffderb/bin/tape-migration/migrate_helper_scripts')
sys.path.append('/home/users/jeffderb/bin/tape-migration')

migrationLogs.too_many_logs('test', list('VPV008'))

