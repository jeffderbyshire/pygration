""" pygration doc string

This program is created to help build automation for tape migration.

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
    """ Parse command arguments, build server list and run commands """
    set_logging(kwargs['debug'])
    fetch_logs(kwargs['logs'])
    process_logs(kwargs['process'], kwargs['quiet'])
    scan_logs(kwargs['scan'])
    check_logs(kwargs['check'], kwargs['quiet'])


main()

exit()
