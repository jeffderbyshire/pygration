""" pygration doc string

This program is created to help build automation for tape migration.
Processes CLI arguments using click.
Required options (choose only 1):
    pygration.py --check
        1. Check unparsed logs for errors.
        2. Find volume serial from end of first line.
        3. Append volume serial and if error append '.0'.
    pygration.py --logs <type>
        1. Find all migration logs or find logs of given type.
        a. Types:
            1. 'all' (default)
            2. 'errors' log file ends in '.0'
            3. 'no-errors' log file has neither volume serial or '.0' appended
            4. 'archive' has volume serial appended without error '.0'
            5. 'archive-with-errors' log file has error '.0' appended, but volume serial has been
                successfully migrated.
    pygration.py --process <option>
        1. Process log files and sort into archive, rerun, or too many errors.
            by reading error messages and grouping into either rerun or too many.
            a. If rerun, build rerun script with first line of log file for a unique set of source
                volumes.
                1. Rerun script /tmp/migrate.rerun
                    a. Start reruns with bash alias 'semr'
            b. For archive, check enstore command if volume serial has been migrated, plus other
                checks to verify migration, then mark the log file to be migrated even it log file
                has error '.0'.
            b. Other error messages are marked too many errors and need a bug report or in the case
                of a new error and its rerun error, need to add error snippet to list of rerun
                errors: parse_logs.py add message snippet to known errors and rerun errors.
        2. Process also cleans spool error of volume serials that have already been migrated
"""
import logging
import logging.handlers
import pprint
import socket
from configparser import ConfigParser
import click
import migrate_helper_scripts.migration_logs as migration_logs
import migrate_helper_scripts.list_logs as list_logs
import migrate_helper_scripts.error_check as error_check
import migrate_helper_scripts.migration_status as migration_status
import migrate_helper_scripts.fix_archives as fix_archives
import migrate_helper_scripts.unity as unity
import migrate_helper_scripts.build_scan as build_scan
import migrate_helper_scripts.clean_spool as clean_spool

CONFIG = ConfigParser()
CONFIG.read('config/config.conf')
LOG_DIR = CONFIG['Default']['log_dir']


def set_logging(debug_flag=False):
    """ set logging and level """
    logging.root.handlers = []
    basic_handler = [
        logging.handlers.TimedRotatingFileHandler(
            filename=LOG_DIR + "/reruns/migration.log",
            when='midnight',
            interval=1,
            backupCount=7
        )
    ]
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                        level=logging.INFO,
                        handlers=basic_handler)
    if debug_flag:
        logging.getLogger().setLevel('DEBUG')


def fetch_logs(log_flag=False):
    """ Fetch logs if log flag is set from cli """
    if log_flag:
        pprint.pprint(list_logs.get_logs(log_flag))


def process_logs(process_flag=False, quiet_flag=False):
    """ Process logs if flag is set and observe quiet flag """
    if process_flag in ['all', 'fix', 'spool', 'status']:
        if not quiet_flag:
            migration_status.report_status()
        if process_flag == 'fix':
            fix_archives.main()
        elif process_flag == 'spool':
            clean_spool.clean(quiet_flag)
        elif process_flag == 'all':
            migration_logs.process(server=socket.gethostname(), quiet=quiet_flag, rerun=True)
            clean_spool.clean(quiet_flag)
        if not quiet_flag:
            migration_status.report_status()

    if process_flag in ['import']:
        unity.db_import(quiet_flag)


def scan_logs(scan_flag=False):
    """ Build scan file if flag is set """
    if scan_flag:
        build_scan.scan(scan_flag)


def check_logs(check_flag=True, quiet_flag=False):
    """ Check logs if flag set and observe quiet flag """
    if check_flag:
        output = error_check.main()
        if not quiet_flag:
            pprint.pprint(output, indent=4)


@click.command()
@click.option('--check', is_flag=True)
@click.option('--debug', is_flag=True)
@click.option('--logs', type=click.Choice(['all', 'errors', 'no-errors', 'archive',
                                           'archive-with-errors']))
@click.option('--process', type=click.Choice(['all', 'fix', 'spool', 'status', 'import']))
@click.option('--quiet', is_flag=True)
@click.option('--scan', nargs=1)
def main(**kwargs):
    """ Pass command arguments to functions """
    set_logging(kwargs['debug'])
    fetch_logs(kwargs['logs'])
    process_logs(kwargs['process'], kwargs['quiet'])
    scan_logs(kwargs['scan'])
    check_logs(kwargs['check'], kwargs['quiet'])


main()

exit()
