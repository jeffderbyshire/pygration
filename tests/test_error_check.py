""" test reading log file """

import configparser

CONFIG = configparser.ConfigParser()
CONFIG.read('config/config.conf')
MIGRATION_DIR = CONFIG['Default']['log_dir']
LOG_FILE_TEST = CONFIG['Default']['log_file_test']


def test_last_5_lines():
    """ print last 5 lines """
    print(MIGRATION_DIR + LOG_FILE_TEST)
    with open(MIGRATION_DIR + LOG_FILE_TEST, 'rb') as handle:
        last_lines = handle.readlines()[-6:]
        print(last_lines)
    for line in last_lines:
        last = line.decode().split()
        print(last)


if __name__ == '__main__':
    test_last_5_lines()
