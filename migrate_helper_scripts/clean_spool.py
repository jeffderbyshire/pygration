""" clean spool area for volumes that have migrated """

import logging
import glob
from os import scandir, path, unlink
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
        dir_path = '/data/data' + str(number) + SPOOL_DIRECTORY
        if path.isdir(dir_path):
            with scandir(dir_path) as the_dir:
                for file in tqdm(the_dir, desc='Checking Spool', disable=quiet):
                    volume_serials.add(file.name.split(':')[0])
                logging.info("spool contains %s volumes", len(volume_serials))
                for volume in tqdm(volume_serials, desc='Checking volumes', disable=quiet):
                    if database.volume_is_migrated(volume) \
                            or parse_logs.check_migration_status(volume):
                        logging.info("cleaning spool of volume:%s", volume)
                        map(unlink, glob.glob(dir_path + volume + '*'))


if __name__ == "__main__":
    clean(False)
