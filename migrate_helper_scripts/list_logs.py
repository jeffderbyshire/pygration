""" list log files in migration directory """

from os import stat, scandir
from pprint import pprint
from datetime import datetime, timedelta
from sys import argv
from configparser import ConfigParser

CONFIG = ConfigParser()
CONFIG.read('config/config.conf')

LOG_DIRECTORY = CONFIG['Default']['log_dir']
LOG_PREFIX = CONFIG['Default']['log_prefix']
VOLUME_SERIAL_PREFIX = CONFIG['List']['volume_serial_prefix']
FILE_MTIME_SHORT = timedelta(hours=12).total_seconds()
FILE_MTIME_LONG = timedelta(days=2).total_seconds()


def check_file_mtime(file_name, age):
    """ check modified time of file """
    now = datetime.now()
    mtime = stat(LOG_DIRECTORY + file_name).st_mtime
    return bool(now.timestamp() - age > mtime)


def find_files(volume_serials, file_age):
    """ find files in log directory that look like MigrationLog and have a mtime """
    files_found = []
    with scandir(LOG_DIRECTORY) as the_dir:
        for file in the_dir:
            if LOG_PREFIX in file.name and check_file_mtime(file.name, file_age):
                if volume_serials:
                    for volume in volume_serials:
                        if volume in file.name:
                            files_found.append(file.name)
                else:
                    files_found.append(file.name)
    return files_found


def vol_prefix_in_file(file_name):
    """ search volume in set of prefixes"""
    for vol_prefix in VOLUME_SERIAL_PREFIX.split('|'):
        print(vol_prefix)
        if vol_prefix in file_name:
            return True

    return False


def select_specific_files(selection, file_list):
    """ selected files """
    selected = []
    for file in file_list:
        if selection == "errors":
            if file.endswith(".0"):
                if vol_prefix_in_file(file):
                    selected.append(file)
        elif selection == "no-errors":
            print(file)
            if not file.endswith(".0"):
                if not vol_prefix_in_file(file):
                    selected.append(file)
        elif selection == "archive":
            if not file.endswith(".0"):
                if vol_prefix_in_file(file):
                    selected.append(file)
        elif selection == "archive-with-errors":
            if vol_prefix_in_file(file):
                selected.append(file)

    return selected


def select_files(selection, file_list):
    """ select files based on command """
    if selection == "all":
        selected = file_list

    else:
        selected = select_specific_files(selection, file_list)
    return selected


def get_logs(command="all", volumes=False):
    """ main function determine file age if archiving """
    if not volumes:
        volumes = set()
    file_modified = FILE_MTIME_SHORT
    if command in {'archive', 'archive-with-errors'}:
        file_modified = FILE_MTIME_LONG
    selected_files = select_files(command, find_files(volumes, file_modified))

    return sorted(selected_files, reverse=True)


if __name__ == '__main__':
    FILES = get_logs(argv[1])
    pprint(FILES, indent=1)
