""" list log files in migration directory """

from os import stat, listdir
from pprint import pprint
from datetime import datetime, timedelta
from sys import argv

LOG_DIRECTORY = "/var/migration/"
LOG_PREFIX = "MigrationLog"
VOLUME_SERIAL_PREFIX = {"-V", "-P", "-I"}
FILE_MTIME_SHORT = timedelta(hours=12).total_seconds()
FILE_MTIME_LONG = timedelta(days=2).total_seconds()


def check_file_mtime(file_name, age):
    """ check modified time of file """
    now = datetime.now()
    mtime = stat(LOG_DIRECTORY + file_name).st_mtime
    return bool(now.timestamp() - age > mtime)


def find_files(volume_serials, file_age):
    """ find files """
    file_names = listdir(LOG_DIRECTORY)
    file_names.sort()
    files_found = []
    for file in file_names:
        if LOG_PREFIX in file:
            if check_file_mtime(file, file_age):
                if len(volume_serials) > 0:
                    for volume in volume_serials:
                        if volume in file:
                            files_found.append(file)
                else:
                    files_found.append(file)

    return files_found


def vol_prefix_in_file(file_name):
    for vol_prefix in VOLUME_SERIAL_PREFIX:
        return bool(vol_prefix in file_name)


def select_files(selection, file_list):
    selected = []
    if selection == "all":
        selected = file_list

    else:
        for file in file_list:
            if selection == "errors":
                if file.endswith(".0"):
                    selected.append(file)
            elif selection == "no-errors":
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


def get_logs(command="all", volumes=False):
    if not volumes:
        volumes = set()
    file_modified = FILE_MTIME_SHORT
    if command in {'archive', 'archive-with-errors'}:
        file_modified = FILE_MTIME_LONG
    selected_files = select_files(command, find_files(volumes, file_modified))

    return sorted(selected_files, reverse=True)


if __name__ == '__main__':
    files = get_logs(argv[1])
    pprint(files, indent=1)
