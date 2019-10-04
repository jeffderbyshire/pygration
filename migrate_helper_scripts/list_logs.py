#!/home/users/jeffderb/python3/bin/python3

import os
import argparse
import textwrap
import pprint
import datetime
import sys

LOG_DIRECTORY = "/var/migration/"
LOG_PREFIX = "MigrationLog"
VOLUME_SERIAL_PREFIX = ["-V", "-P", "-I"]
FILE_MTIME_SHORT = datetime.timedelta(hours=12).seconds
FILE_MTIME_LONG = datetime.timedelta(days=2).seconds


def usage():
    print("usage: list_logs.py [ all | errors | no-errors | archive | archive_with_errors "
          + "| volumes A [B C ... N]]")


def check_file_mtime(file_name, age):
    now = datetime.datetime.now()
    mtime = os.stat(LOG_DIRECTORY + file_name).st_mtime
    if now.timestamp() - age > mtime:
        return True

    return False


def find_files(volume_serials, file_age):
    file_names = os.listdir(LOG_DIRECTORY)
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
        if vol_prefix in file_name:
            return True

    return False


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
        volumes = []
    file_modified = FILE_MTIME_SHORT
    if command in ['archive', 'archive-with-errors']:
        file_modified = FILE_MTIME_LONG
    selected_files = select_files(command, find_files(volumes, file_modified))

    return selected_files


if __name__ == '__main__':
    files = get_logs(sys.argv[1])
    pprint.pprint(files, indent=1)
