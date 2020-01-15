""" fix archives """

import os
from glob import glob
from configparser import ConfigParser
from tqdm import tqdm
import migrate_helper_scripts.parse_logs as parse_logs

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
        print(log)
        try:
            volume = log.split(LOG_PREFIX)[1].split('-')[3].split('.')[0]
        except IndexError:
            volume = 'XXX'
        print(volume)
        if 'VP' in volume[:2] or 'P' in volume[0] or 'I' in volume[0]:
            if not parse_logs.check_migration_status(volume):
                volumes.add(volume)

    return volumes


def move_archived_logs(volumes):
    """ move archived logs back to main log directory """
    for volume in volumes:
        for log in glob(LOG_DIRECTORY + ARCHIVE_DIR + '*/*/*' + volume + '.0.gz'):
            file_name = log.split('/')[-1]
            os.rename(log, LOG_DIRECTORY + file_name)


def main():
    """ main function """
    volumes = get_volume_from_archive()
    move_archived_logs(volumes)


if __name__ == "__main__":
    main()
