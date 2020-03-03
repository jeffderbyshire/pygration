""" Import unity db files into postgres db """

from datetime import datetime
from configparser import ConfigParser
from tqdm import tqdm
import migrate_helper_scripts.database_schema as database

CONFIG = ConfigParser()
CONFIG.read('config/config.conf')
UNITY_DIR = CONFIG['Unity_Import']['unity_dir']
SCAN_DBS = CONFIG['Unity_Import']['scan_dbs'].split('|')
STATE_DBS = CONFIG['Unity_Import']['state_dbs'].split('|')


def db_import(quiet=False):
    """ main function parse unity db files and insert or update dbs """
    format_date = '%Y%m%d'
    for scan_file in SCAN_DBS:
        with open(UNITY_DIR + scan_file) as file:
            for line in tqdm(file.readlines(), disable=quiet, desc='import ' + scan_file):
                record = {}
                line = line.split(':')
                record['scan_volume'] = line[0]
                try:
                    record['scan_start'] = datetime.strptime(line[1], format_date)
                except ValueError:
                    record['scan_start'] = None
                record['scan_node'] = line[2]
                record['scan_errors'] = line[3]
                try:
                    record['scan_end'] = datetime.strptime(line[4], format_date)
                except ValueError:
                    record['scan_end'] = None
                record['source_list'] = line[5]
                database.insert_update_migration_scan(record)

    for migration_file in STATE_DBS:
        with open(UNITY_DIR + migration_file) as file:
            for line in tqdm(file.readlines(), disable=quiet, desc='import ' + migration_file):
                record = {}
                line = line.split(':')
                record['source_volume'] = line[0]
                record['media'] = line[1]
                record['migration_type'] = line[2]
                try:
                    record['migration_start'] = datetime.strptime(line[8], format_date)
                except ValueError:
                    record['migration_start'] = None
                record['node'] = line[9]
                record['errors'] = line[10]
                try:
                    record['migration_end'] = datetime.strptime(line[11], format_date)
                except ValueError:
                    record['migration_end'] = None
                record['destination_volumes'] = line[12]
                try:
                    record['scanned'] = datetime.strptime(line[13], format_date)
                except ValueError:
                    record['scanned'] = None
                record['storage_group'] = line[20]
                record['library'] = line[22]
                record['file_family'] = line[21]
                database.insert_update_migration_state(record)


if __name__ == '__main__':
    db_import()
