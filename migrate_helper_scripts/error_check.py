""" check log files for errors """

import os
import logging
import configparser
import migrate_helper_scripts.list_logs as list_logs
import migrate_helper_scripts.check_running as check_running

CONFIG = configparser.ConfigParser()
CONFIG.read('config/config.conf')
MIGRATION_DIR = CONFIG['Default']['log_dir']
VOLUME_SERIAL_PREFIX = CONFIG['List']['volume_serial_prefix']


def validate_volume(volume_name):
    """ validate volume name from config file """
    for vol_prefix in VOLUME_SERIAL_PREFIX.split('|'):
        if volume_name.startswith(vol_prefix.strip('-')):
            return True

    logging.info("%s: Cannot validate %s", __file__, volume_name)
    return False


def main():
    """ look for new log files and check for errors.  rename file with volume serial """
    output_renames = {}
    check_running.main()
    unchecked_files = list_logs.get_logs("no-errors")
    for file in unchecked_files:
        file_name = MIGRATION_DIR + file
        output_renames[file_name] = ''
        error = ".0"
        volume = ''
        with open(file_name, 'rb') as handle:
            first = next(handle).decode().split()
            if validate_volume(first[-1]):
                volume = '-' + first[-1]

            if os.path.getsize(file_name) > 1024:
                file_size = 1024
            else:
                file_size = int(os.path.getsize(file_name))
            handle.seek(-1 * file_size, 2)
            last_lines = handle.readlines()[-6:]
            for line in last_lines:
                last = line.decode().split()
                if len(last) > 8:
                    if (last[7] + last[8]) == "setcomment":
                        break
            else:
                volume = volume + error
        dst_file_name = file_name + volume
        os.rename(file_name, dst_file_name)
        output_renames[file_name] = dst_file_name

    return output_renames


if __name__ == '__main__':
    main()
