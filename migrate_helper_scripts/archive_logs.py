""" archive logs """
import gzip
import shutil
import collections
import os
from configparser import ConfigParser
from tqdm import tqdm
import migrate_helper_scripts.list_logs as list_logs
import migrate_helper_scripts.database_schema as database

CONFIG = ConfigParser()
CONFIG.read('config/config.conf')
LOG_DIRECTORY = CONFIG['Default']['log_dir']
LOG_PREFIX = CONFIG['Default']['log_prefix']
ARCHIVE_DIR = CONFIG['Archive']['archive_dir']


def get_year_month(log_name):
    """ parse year and month from log file name """
    log_name = log_name.replace(LOG_PREFIX, '')
    return "/".join(log_name.split('-')[0:2])


def remove_db_entries(volumes):
    """ connect to sqlite db and remove entries with volume serials that were archived """
    total = 0
    for volume in tqdm(volumes, desc='Delete from db'):
        total += database.delete_volume_name(volume)
    return total


def archive(command="archive", volumes=False):
    """ main archive function
    make path with LOG Directory / year / month
    gzip log file and mv to archive path and delete log file
    search and delete volume serial from sqlite error log db """
    logs = list_logs.get_logs(command, volumes)
    totals = collections.Counter()
    volumes = []
    if logs:
        for log in tqdm(logs, desc='Archive Logs:'):
            year_month = get_year_month(log)
            os.makedirs(LOG_DIRECTORY + ARCHIVE_DIR + year_month, exist_ok=True)
            log_file_path = LOG_DIRECTORY + log
            if os.path.exists(log_file_path):
                totals['log count'] += 1
                gz_file_path = LOG_DIRECTORY + ARCHIVE_DIR + year_month + '/' + log + '.gz'
                with open(log_file_path, 'rb') as f_in:
                    with gzip.open(gz_file_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                        totals['archived'] += 1
                if os.path.exists(gz_file_path):
                    with open(log_file_path, 'rb') as handle:
                        try:
                            volumes.append(next(handle).decode().split()[-1])
                        except StopIteration:
                            pass

                    os.remove(log_file_path)
                    totals['removed'] += 1

    else:
        return {'logs found': logs}

    totals['db_removed'] = remove_db_entries(volumes)

    return totals


if __name__ == '__main__':
    archive()
