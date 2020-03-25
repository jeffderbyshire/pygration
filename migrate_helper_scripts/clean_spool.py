""" clean spool area for volumes that have migrated """

import logging
from pathlib import Path
from configparser import ConfigParser
from tqdm import tqdm
import migrate_helper_scripts.parse_logs as parse_logs
import migrate_helper_scripts.database_schema as database

CONFIG = ConfigParser()
CONFIG.read('config/config.conf')

SPOOL_DIRECTORY = CONFIG['Default']['spool_dir']


def clean(quiet=False):
    """ check migration spool, find volumes and check migration status, then unlink """
    volume_serials = set()
    for number in range(1, 4):
        try:
            dir_path = Path('/data/data' + str(number) + SPOOL_DIRECTORY)
        except OSError:
            continue
        for the_dir in dir_path.iterdir():
            for file in tqdm(the_dir, desc='Checking Spool', disable=quiet):
                print(file)
                exit()
                volume_serials.add(file.name.split(':')[0])
            logging.info("spool contains %s volumes", len(volume_serials))
            for volume in tqdm(volume_serials, desc='Checking volumes', disable=quiet):
                if database.volume_is_migrated(volume) \
                        or parse_logs.check_migration_status(volume):
                    logging.info("cleaning spool of volume:%s", volume)
                    for spool_file in dir_path.glob('/' + volume + '*'):
                        spool_file.unlink()


if __name__ == "__main__":
    clean(False)
