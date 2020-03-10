""" check processes running
    check disk space
    check unprocessed logs
    count of volume serials in archive
    count of volume serials with errors
"""

import subprocess
from shutil import disk_usage
from configparser import ConfigParser
from pprint import pprint
from glob import iglob
import migrate_helper_scripts.check_running as check_running
import migrate_helper_scripts.list_logs as list_logs

CONFIG = ConfigParser()
CONFIG.read('config/config.conf')
LOG_DIRECTORY = CONFIG['Default']['log_dir']
LOG_PREFIX = CONFIG['Default']['log_prefix']
ARCHIVE_DIR = CONFIG['Archive']['archive_dir']


def fetch_df_mounts():
    """ fetch df mounts """
    output = {"pnfs": set(), "var": list(), "header": list(), "data": set()}
    pnfs_mount = subprocess.run(
        [
            'df',
            '-h'
        ],
        timeout=5,
        caputure_output=True
    )
    for row in pnfs_mount.stdout.decode():
        if 'Filesystem' in row:
            output['header'] = row.split()
        elif 'var' in row:
            output['var'] = row.split()
        elif 'data' in row:
            output['data'].add(row.split())
        elif 'pnfs' in row:
            output['pnfs'].add((row.split()[0], row.split()[-1]))

    return output


def check_uptime():
    """ check uptime and return """
    uptime_result = subprocess.run(
        [
            'uptime'
        ],
        timeout=5,
        capture_output=True
    )
    return uptime_result.stdout.decode()


def check_disk_space():
    """ check disk space and return {path: disk space used} """
    storage = {}
    for i in range(1, 4):
        path = '/data/data' + str(i)
        try:
            usage = disk_usage(path)
            storage[path] = '{:2f} %'.format((usage.used / usage.total) * 100)
        except FileNotFoundError:
            pass

    return storage


def fetch_archived_logs():
    """ look in archive and return {volume_serials} """
    archive = set()
    for log in iglob(LOG_DIRECTORY + ARCHIVE_DIR + '/*/*/' + LOG_PREFIX + '*.gz',
                     recursive=True):
        archive.add(log.split('-')[-1].split('.')[0])
    return archive


def count_error_logs():
    """ count distinct volume serials in error logs """
    errors = set()
    for log in list_logs.get_logs('errors'):
        errors.add(log.split('-')[-1])
    return errors


def report_status():
    """ print and call """
    pprint({'running': len(check_running.main()[0]),
            'disk space': check_disk_space(),
            'unprocessed logs': len(list_logs.get_logs('no-errors')),
            'archived': len(fetch_archived_logs()),
            'errors': len(count_error_logs())})
