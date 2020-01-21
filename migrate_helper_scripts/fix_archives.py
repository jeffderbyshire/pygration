""" fix archives """

import os
from datetime import datetime
from glob import glob
from configparser import ConfigParser
from tqdm import tqdm
import migrate_helper_scripts.parse_logs as parse_logs
from migrate_helper_scripts.database_schema import insert_migrated, volume_is_migrated
from migrate_helper_scripts.list_logs import vol_prefix_in_file

CONFIG = ConfigParser()
CONFIG.read('config/config.conf')
LOG_PREFIX = CONFIG['Default']['log_prefix']
LOG_DIRECTORY = CONFIG['Default']['log_dir']
ARCHIVE_DIR = CONFIG['Archive']['archive_dir']


def get_volume_from_archive():
    """ get volume serials from archive logs """
    volumes = set()
    for log in tqdm(glob(LOG_DIRECTORY + ARCHIVE_DIR + '*/*/*.0.gz'), desc='check archive logs'):
        # MigrationLog@2019-12-04.12:29:59#336614-VP5615.0.gz
        try:
            volume = log.split(LOG_PREFIX)[1].split('-')[3].split('.')[0]
        except IndexError:
            volume = 'XXX'
        if len(volume) > 3 and not volume_is_migrated(volume):
            if vol_prefix_in_file(volume):
                if parse_logs.check_migration_status(volume):
                    insert_migrated(volume)
                else:
                    volumes.add(volume)

    return volumes


def fix_mtime(log):
    """ fix modified time for files based on log file name """
    date_time = parse_logs.get_date_time(log)
    mtime = datetime.strptime(date_time['date'] + 'T' + date_time['time'],
                              '%Y-%m-%dT%H:%M:%S').timestamp()
    os.utime(log, (mtime, mtime))


def move_archived_logs(volumes):
    """ move archived logs back to main log directory """
    for volume in volumes:
        for log in glob(LOG_DIRECTORY + ARCHIVE_DIR + '*/*/*' + volume + '.0.gz'):
            file_name = log.split('/')[-1]
            os.rename(log, LOG_DIRECTORY + file_name)


def main():
    """ main function """
    with os.scandir(LOG_DIRECTORY) as the_dir:
        for file in the_dir:
            if LOG_PREFIX in file.name and file.name.endswith('.0'):
                fix_mtime(LOG_DIRECTORY + file.name)
    volumes = get_volume_from_archive()
    move_archived_logs(volumes)


if __name__ == "__main__":
    main()
