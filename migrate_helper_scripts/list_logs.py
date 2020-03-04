""" list log files in migration directory """

from os import stat, scandir
from pprint import pprint
from datetime import datetime, timedelta
from sys import argv
from configparser import ConfigParser
import migrate_helper_scripts.check_running as check_running

CONFIG = ConfigParser()
CONFIG.read('config/config.conf')

LOG_DIRECTORY = CONFIG['Default']['log_dir']
LOG_PREFIX = CONFIG['Default']['log_prefix']
VOLUME_SERIAL_PREFIX = CONFIG['List']['volume_serial_prefix']
FILE_MTIME_LONG = timedelta(days=1).total_seconds()


def check_running_process(file_name):
    """ check log file based on running process """
    for process in check_running.main()[1]:
        if process in file_name.split('#')[1]:
            return True
    return False


def check_file_mtime(file_name, age):
    """ check modified time of file """
    now = datetime.now()
    mtime = stat(LOG_DIRECTORY + file_name).st_mtime
    return bool(now.timestamp() - age > mtime)


def find_files(volume_serials):
    """ find files in log directory that look like MigrationLog and aren't running process """
    files_found = []
    with scandir(LOG_DIRECTORY) as the_dir:
        for file in the_dir:
            if LOG_PREFIX in file.name and not check_running_process(file.name):
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
        if vol_prefix in file_name:
            return True

    return False


def log_file_has_volume_serial(file):
    """ check if log file has -VolumeSerial appended """
    if "#" not in file:
        return False

    return bool("-" in file.split('#')[1])


def select_specific_files(selection, file_list):
    """ selected files """
    selected = []
    for file in file_list:
        if selection == "errors":
            if file.endswith(".0"):
                if vol_prefix_in_file(file):
                    selected.append(file)
        elif selection == "no-errors":
            if not file.endswith(".0"):
                if not log_file_has_volume_serial(file):
                    selected.append(file)
        elif selection in ["archive", "archive-with-errors"]:
            if log_file_has_volume_serial(file) and check_file_mtime(file, FILE_MTIME_LONG):
                if selection == "archive":
                    if not file.endswith(".0"):
                        selected.append(file)
                else:
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
    """ main function find files and return sorted list """
    if not volumes:
        volumes = set()
    selected_files = select_files(command, find_files(volumes))

    return sorted(selected_files, reverse=True)


if __name__ == '__main__':
    FILES = get_logs(argv[1])
    pprint(FILES, indent=1)
