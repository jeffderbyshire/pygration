""" Process logs

Main command line is --process see_errors
Parses logs for volume serials to archive, rerun, and too many errors
store too many errors in sqlite db
"""
import pprint
from configparser import ConfigParser
from tqdm import tqdm
import migrate_helper_scripts.archive_logs as archive_logs
import migrate_helper_scripts.parse_logs as parse_logs
import migrate_helper_scripts.list_logs as list_logs
import migrate_helper_scripts.build_rerun as build_rerun
import migrate_helper_scripts.error_check as error_check
import migrate_helper_scripts.see_errors as see_errors
import migrate_helper_scripts.database_schema as database

CONFIG = ConfigParser()
CONFIG.read('config/config.conf')
LOG_PREFIX = CONFIG['Default']['log_prefix']
LOG_DIR = CONFIG['Default']['log_dir']


def too_many_logs(server, too_many_list):
    """ Connect to sqlite db and insert server, volume serial, and log file details"""
    server_id = database.get_node_id(server)
    for volume in tqdm(too_many_list, desc='> 2 Errors:'):
        volume_id = database.get_volume_id(volume)
        error_logs = list_logs.get_logs("errors", {volume})
        for log_file in error_logs:
            date = log_file.split(LOG_PREFIX)[1].split("#")[0].split(".")[0]
            log_file_id = database.get_log_file_id(server_id, volume_id, log_file, date)
            error_messages = see_errors.error_messages(LOG_DIR + log_file)
            log_details = []
            for message in error_messages:
                log_details.append((log_file_id, parse_logs.interpret_error_message(message),
                                    message))

            database.insert_log_file_detail(log_details)


def process(server, item, volume=False, quiet=False):
    """ parse command line arguments and run functions """
    archive_count = rerun_logs = 0
    output = {}
    logs = {}
    if item == "check":
        output = error_check.main()

    elif item in {'archive', 'archive_with_errors'}:
        output = archive_logs.archive(item, volume)

    elif item == "see_errors":
        archive_logs.archive("archive")
        output = see_errors.see_errors()
        logs = parse_logs.parse_logs(output)
        if logs['archive']:
            # pprint.pprint(archive)
            archive_count = archive_logs.archive("archive-with-errors", sorted(logs['archive']))
            # pprint.pprint(list_logs.get_logs('archive-with-errors', sorted(archive)))
        if logs['rerun']:
            rerun_logs = build_rerun.rerun(logs['rerun'])
        if logs['too_many']:
            # print("More than 2 errors:")
            # pprint.pprint(too_many, indent=1)
            # pprint.pprint(counter, indent=1)
            too_many_logs(server, sorted(logs['too_many']))

    if not quiet:
        print('Node: ' + server)
        print('Process: ' + item)
        print("archive: " + str(len(logs['archive'])))
        print("rerun: " + str(len(logs['rerun'])))
        print("too many: " + str(len(logs['too_many'])))
        print("Archive processed")
        pprint.pprint(archive_count, indent=1)
        print("Rerun processed")
        pprint.pprint(rerun_logs['msg'][0], indent=1)
        pprint.pprint(rerun_logs['rerun'], indent=1)
        if item != "see_errors":
            pprint.pprint(output, indent=4)
        print('End of line.')
