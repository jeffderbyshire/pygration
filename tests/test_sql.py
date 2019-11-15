import sys
from migrate_helper_scripts import migration_logs

sys.path.append('/home/users/jeffderb/bin/tape-migration/migrate_helper_scripts')
sys.path.append('/home/users/jeffderb/bin/tape-migration')

migration_logs.too_many_logs('test', ['VPV008'])

