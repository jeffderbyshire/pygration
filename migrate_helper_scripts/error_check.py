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


def validate_volume(head_words):
    """ validate volume name from config file """
    for vol_prefix in VOLUME_SERIAL_PREFIX.split('|'):
        for word in reversed(head_words):
            if word.startswith(vol_prefix.strip('-')):
                return '-' + word

    logging.info("%s: Can't find suitable volume in %s", __file__, head_words)
    return '---'


def main():
    """ look for new log files and check for errors.  rename file with volume serial """
    output_renames = {}
    check_running.main()
    unchecked_files = list_logs.get_logs("no-errors")
    for file in unchecked_files:
        file_name = MIGRATION_DIR + file
        output_renames[file_name] = ''
        error = ".0"
        with open(file_name, 'rb') as handle:
            first = next(handle, 'End of File'.encode()).decode().split()
            volume = validate_volume(first[7:])

            if os.path.getsize(file_name) > 1024:
                file_size = 1024
            else:
                file_size = int(os.path.getsize(file_name))
            handle.seek(-1 * file_size, 2)
            last_lines = handle.readlines()[-6:]
            for line in last_lines:
                last = line.decode().split()
                if len(last) > 8:
                    if ((last[7] + last[8]) == "setcomment") or \
                            (last[6] + last[7] == "successfullymigrated"):
                        break
            else:
                volume = volume + error
        # Can be:
        # file_name + VOL_SER
        # file_name + VOL_SER + '.0'
        # file_name + '---' +/- '.0'  Can't find valid VOL_SER in "head -1 log_file"
        dst_file_name = file_name + volume
        os.rename(file_name, dst_file_name)
        output_renames[file_name] = dst_file_name

    return output_renames


if __name__ == '__main__':
    main()
