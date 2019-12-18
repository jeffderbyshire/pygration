""" Process logs

Main command line is --process see_errors
Parses logs for volume serials to archive, rerun, and too many errors
store too many errors in sqlite db
"""
import pprint
import subprocess
from configparser import ConfigParser
from tqdm import tqdm
import migrate_helper_scripts.archive_logs as archive_logs
import migrate_helper_scripts.parse_logs as parse_logs
import migrate_helper_scripts.list_logs as list_logs
import migrate_helper_scripts.build_rerun as build_rerun
import migrate_helper_scripts.see_errors as see_errors
import migrate_helper_scripts.database_schema as database

CONFIG = ConfigParser()
CONFIG.read('config/config.conf')
LOG_PREFIX = CONFIG['Default']['log_prefix']
LOG_DIR = CONFIG['Default']['log_dir']


def too_many_logs(server, too_many_list):
    """ Connect to sqlite db and insert server, volume serial, and log file details"""
    volume_dict = {'bfid': set(), 'pnfs': set(), 'server_id': database.get_node_id(server)}
    all_volumes = {}
    for volume in tqdm(too_many_list, desc='> 9 Errors:'):
        volume_dict['volume_id'] = database.get_volume_id(volume)
        error_logs = list_logs.get_logs("errors", {volume})
        for log_file in error_logs:
            date = log_file.split(LOG_PREFIX)[1].split("#")[0].split(".")[0]
            log_file_id = database.get_log_file_id(volume_dict['server_id'],
                                                   volume_dict['volume_id'], log_file, date)
            error_messages = see_errors.error_messages(LOG_DIR + log_file)
            log_details = []
            for message in error_messages:
                # print(message.split())
                for log_word in message.split():
                    if 'CDMS' in log_word:
                        volume_dict['bfid'].add(log_word)
                    if '/pnfs' in log_word:
                        volume_dict['pnfs'].add(log_word)
                log_details.append((log_file_id, parse_logs.interpret_error_message(message),
                                    message))

            database.insert_log_file_detail(log_details)
        all_volumes[volume] = volume_dict
    return all_volumes


def file_migration_status(bfid):
    """ Run migrate --status command and Return status of bfid """
    try:
        status = subprocess.run(
            [
                '/opt/enstore/Python/bin/python',
                '/opt/enstore/bin/migrate',
                '--status',
                bfid
            ],
            capture_output=True)
        status = status.stdout.decode()
    except FileNotFoundError:
        status = ''
    return status


def detail_error_messages(all_dict):
    """ receive error list and run enstore commands against volume serials, bfids, and pnfs """
    error_details = {}
    bfid_reason = {}
    for volume in all_dict:
        # pprint.pprint(volume)
        # pprint.pprint(all_dict[volume])
        for bfid in tqdm(all_dict[volume]['bfid'], desc='testing bfids'):
            status = file_migration_status(bfid)
            if 'MUTIPLE_COPY' in status:
                reason = 'MULTIPLE_COPY'
            else:
                reason = 'Unknown'
            bfid_reason[bfid] = reason
        error_details[volume] = bfid_reason
    return error_details


def process(server, quiet=False):
    """ parse command line arguments and run functions """
    archive_count = 0
    rerun_logs = {}
    all_errors = {}
    archive_logs.archive("archive")
    output = see_errors.see_errors()
    logs = parse_logs.parse_logs(output)
    if logs['archive']:
        archive_count = archive_logs.archive("archive-with-errors", sorted(logs['archive']))
    if logs['rerun']:
        rerun_logs = build_rerun.rerun(logs['rerun'])
    if logs['too_many']:
        all_errors = too_many_logs(server, sorted(logs['too_many']))
        pprint.pprint(detail_error_messages(all_errors), width=100, depth=5)

    if not quiet:
        print('Node: ' + server)
        print("archive: " + str(len(logs['archive'])))
        print("rerun: " + str(len(logs['rerun'])))
        print("too many: " + str(len(logs['too_many'])))
        print("Archive processed")
        pprint.pprint(archive_count, indent=1)
        print("Rerun processed")
        pprint.pprint(rerun_logs['msg'], indent=1)
        pprint.pprint(rerun_logs['rerun'], indent=1)
        print('End of line.')
