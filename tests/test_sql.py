import sys
import migrate_helper_scripts

sys.path.append('/home/users/jeffderb/bin/tape-migration/migrate_helper_scripts')
sys.path.append('/home/users/jeffderb/bin/tape-migration')

migrate_helper_scripts.migrationLogs.too_many_logs('test', list('VPV008'))

