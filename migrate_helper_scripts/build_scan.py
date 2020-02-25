""" build scan script """

import logging
from configparser import ConfigParser
from tqdm import tqdm
import migrate_helper_scripts.database_schema as database
import migrate_helper_scripts.build_rerun as build_rerun

CONFIG = ConfigParser()
CONFIG.read('config/config.conf')
SCAN_SCRIPT_DIR = CONFIG['Default']['log_dir'] + 'scans/'


def scan(storage_group):
    """ build scan script and run if < 2 processes running """
    commands = {}
    volumes = database.get_volumes_need_scanning(storage_group)
    logging.info("storage group %s volumes %s", storage_group, volumes)
    for file_family, volumes in tqdm(volumes.items(), desc='Build Scan'):
        for volume in volumes:
            commands[volume] = '/opt/enstore/src/migrate_chimera.py --scan --check-only-meta'
        build_rerun.write_run_file(commands, SCAN_SCRIPT_DIR + file_family, "scan")
        logging.info("file family %s with volumes %s", file_family, volumes)


if __name__ == '__main__':
    scan('cms')
