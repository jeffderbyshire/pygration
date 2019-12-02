""" pygration doc string

This program is created to help build automation for tape migration.

TODO add new command status to get disk usage, processes running, and # of logs in log file,
    unprocessed, errors, etc
TODO add status to server, volume serials with errors and volume serial in archive/ save to db

TODO message rerun as set for unique values
"""
import pprint
import socket
import click

import migrate_helper_scripts.migration_logs as migration_logs
import migrate_helper_scripts.list_logs as list_logs
import migrate_helper_scripts.error_check as error_check


@click.command()
@click.option('--logs', type=click.Choice(['all', 'errors', 'no-errors'], case_sensitive=False))
@click.option('--process', is_flag=True)
@click.option('--quiet', is_flag=True)
@click.option('--check', is_flag=True)
def main(logs, process, quiet, check):
    """ Parse command arguments, build server list and run commands """
    server = socket.gethostname()

    if logs:
        pprint.pprint(list_logs.get_logs(logs))

    if process:
        migration_logs.process(server=server, quiet=quiet)

    if check:
        output = error_check.main()
        if not quiet:
            pprint.pprint(output, indent=4)


main()


exit()
