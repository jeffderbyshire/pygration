""" clean spool area for volumes that have migrated """

import logging
from os import scandir, path
from configparser import ConfigParser
from tqdm import tqdm
import migrate_helper_scripts.parse_logs as parse_logs

CONFIG = ConfigParser()
CONFIG.read('config/config.conf')

SPOOL_DIRECTORY = CONFIG['Default']['spool_dir']


def clean(quiet=False):
    """ check migration spool, find volumes and check migration status, then unlink """
    volume_serials = set()
    for number in range(1, 3):
        dir_path = '/data/data' + str(number) + SPOOL_DIRECTORY
        if path.isdir(dir_path):
            with scandir(dir_path) as the_dir:
                for file in tqdm(the_dir, desc='Checking Spool', disable=quiet):
                    volume_serials.add(file.split(':')[0])
                logging.info("clean spool of #%s", len(volume_serials))
                for volume in tqdm(volume_serials, desc='Checking volumes', disable=quiet):
                    if parse_logs.check_migration_status(volume):
                        logging.info("cleaning spool of volume:%s", volume)
                        for file in the_dir:
                            if volume in file:
                                print(dir_path + file)  # unlink(dir_path + file)


if __name__ == "__main__":
    clean(False)
