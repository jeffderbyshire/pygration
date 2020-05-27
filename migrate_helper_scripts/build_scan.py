""" build scan script """

import logging
from configparser import ConfigParser
from tqdm import tqdm
import migrate_helper_scripts.database_schema as database
import migrate_helper_scripts.build_rerun as build_rerun

CONFIG = ConfigParser()
CONFIG.read('config/config.conf')
SCAN_SCRIPT = CONFIG['Scan']['scan_script']
SCAN_VOLUME = CONFIG['Scan']['tape_type']


def scan(storage_group='all'):
    """ build scan script and run if < 2 processes running """
    commands = {}
    if storage_group == 'all':
        storage_groups = database.get_all_storage_groups_for_scanning('cms')
    else:
        storage_groups = set(storage_group)
    for group in tqdm(storage_groups, desc='Build Scan'):
        volumes = database.get_volumes_need_scanning(group)
        logging.debug("storage group %s volumes %s", group, volumes)
        for volume in volumes:
            for valid in SCAN_VOLUME.split('|'):
                if valid in volume:
                    commands[volume] = \
                        '/opt/enstore/src/migrate_chimera.py --scan --check-only-meta'
        logging.info("file family %s with volumes %s", group, volumes)

    build_rerun.write_run_file(commands, SCAN_SCRIPT, storage_group + " scan")


if __name__ == '__main__':
    scan('cms')
