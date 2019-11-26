""" pygration doc string

This program is created to help build automation for tape migration.

Currently, it's a collection of bash scripts with some Python wrapping.  The scripts are uploaded
via rsync and run via ssh and python subprocess.

pygration --server fdm1802 OR omit and parse all servers
pygration logs --no-errors: show logs without errors
pygration logs --errors:    show logs with errors
pygration logs --all:       show all logs
pygration process check:    check logs for errors and rename
pygration process rerun:    build rerun script based on errors TODO: more complete error checking
pygration process archive:  archive processed logs to 'yyyy/mm' folder

Examples: pygration logs --no-errors process check --server fdm1802

TODO use click instead of argparse
TODO add new command status to get disk usage, processes running, and # of logs in log file,
    unprocessed, errors, etc
TODO move prints to final report


"""
import argparse
import pprint
import socket
import textwrap

import migrate_helper_scripts.migration_logs as migration_logs
import migrate_helper_scripts.list_logs as list_logs


def get_args() -> argparse:
    """ Parse command line arguments and return object"""
    parser = argparse.ArgumentParser(description='Process Migration Logs',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--logs', metavar='log_type', nargs=1, default=False,
                        help=textwrap.dedent('''\
                            no-errors:    list logs without errors
                            errors:       show logs with errors
                            all:          show all logs
                            default:        --all
                            '''))
    parser.add_argument('--process', metavar='action', nargs=1, default=False,
                        help=textwrap.dedent('''\
                            check:              look for errors and rename logs
                            rerun:              build rerun script and run inside screen
                            archive:            archive old logs into year / month folders
                            archive_with_errors:archive old (> 2 days) into folders  
                            fix_archives:       fix log names in archived log folders
                            group_errors:       put log files into files with experiments
                            get_volume_serial:  get volume serials
                            default:            do nothing
                            '''))
    parser.add_argument('--server', dest='server', metavar='node', nargs=1, default='all',
                        help='run command(s) on single node')
    parser.add_argument('--quiet', action='store_true',
                        help='suppress output for cron job')
    parser.add_argument('--volumes', metavar='volume_serials', nargs='+', default=False,
                        help='volume serials [ VPXXXX1 VPXXXX2 ... VPXXXXN ]')

    return parser.parse_args()


def main():
    """ Parse command arguments, build server list and run commands """
    args = get_args()
    server = socket.gethostname()
    if args.logs:
        pprint.pprint(list_logs.get_logs(args.logs[0]))
    if args.process:
        migration_logs.process(server=server, item=args.process[0], quiet=args.quiet)


main()


exit()
