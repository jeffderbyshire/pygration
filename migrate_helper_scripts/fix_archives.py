""" fix archives """


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
        volumes.add(log.split(LOG_PREFIX)[1].split('-')[3].split('.')[0])

    return volumes


def check_volumes(volumes):
    """ check volume migration status """
    check_these = volumes
    for volume in check_these:
        if parse_logs.check_migration_status(volume):
            volumes.discard(volume)

    return volumes


def main():
    """ main function """
    volumes = get_volume_from_archive()
    volumes = check_volumes(volumes)
    print(volumes)


if __name__ == "__main__":
    main()
