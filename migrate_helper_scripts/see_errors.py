""" look for ERR in log files and get messages, volume serials, and file names """

import re
from configparser import ConfigParser
import migrate_helper_scripts.list_logs as list_logs

CONFIG = ConfigParser()
CONFIG.read('config/config.conf')
MIGRATION_DIR = CONFIG['Default']['log_dir']


def error_messages(file_name):
    """ search file_name for ERR and return entire message """
    errors = []
    with open(file_name, 'rb') as handle:
        for line in handle.readlines():
            message = line.decode()
            if re.search('ERR', message):
                errors.append(message)

    return errors


def see_errors():
    """ get list of error logs, parse files for errors and get volume serial """
    error_files = list_logs.get_logs("errors")
    all_errors = []
    for file in error_files:
        file_name = MIGRATION_DIR + file
        with open(file_name, 'rb') as handle:
            error_message = ""
            try:
                first = next(handle).decode().split()
                volume = first[-1]
                for line in handle.readlines():
                    message = line.decode()
                    if re.search('ERR', message):
                        error_message = message
                        break
            except StopIteration:
                pass
        error = volume + " ---- " + error_message
        all_errors.append(error)

    # pprint.pprint(all_errors)

    return all_errors


if __name__ == '__main__':
    see_errors()
