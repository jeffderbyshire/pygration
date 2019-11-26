""" pygration doc string

This program is created to help build automation for tape migration.

TODO add new command status to get disk usage, processes running, and # of logs in log file,
    unprocessed, errors, etc
"""
import pprint
import socket
import click

import migrate_helper_scripts.migration_logs as migration_logs
import migrate_helper_scripts.list_logs as list_logs


@click.command()
@click.option('--logs', type=click.Choice(['all', 'errors', 'no-errors'], case_sensitive=False))
@click.option('--process', type=click.Choice(['check', 'see_errors']))
@click.option('--quiet', is_flag=True)
def main(logs, process, quiet):
    """ Parse command arguments, build server list and run commands """
    server = socket.gethostname()

    if logs:
        pprint.pprint(list_logs.get_logs(logs))

    if process:
        migration_logs.process(server=server, item=process, quiet=quiet)


main()


exit()
