""" build scan script """

import logging
import os
import shutil
from configparser import ConfigParser
from tqdm import tqdm
import migrate_helper_scripts.database_schema as database
import migrate_helper_scripts.build_rerun as build_rerun

CONFIG = ConfigParser()
CONFIG.read('config/config.conf')
SCAN_SCRIPT_DIR = CONFIG['Default']['log_dir'] + 'scans/'
DEBUG = False


def scan(storage_group):
    """ build scan script and run if < 2 processes running """
    commands = {}
    if os.path.isdir(SCAN_SCRIPT_DIR):
        shutil.rmtree(SCAN_SCRIPT_DIR)
    os.mkdir(SCAN_SCRIPT_DIR)
    volumes = database.get_volumes_need_scanning(storage_group)
    if DEBUG:
        logging.info("storage group %s volumes %s", storage_group, volumes)
    for volume in tqdm(volumes, desc='Build Scan'):
        commands[volume] = '/opt/enstore/src/migrate_chimera.py --scan --check-only-meta'
    build_rerun.write_run_file(commands, SCAN_SCRIPT_DIR + storage_group, "scan")
    logging.info("file family %s with volumes %s", storage_group, volumes)


if __name__ == '__main__':
    scan('cms')
