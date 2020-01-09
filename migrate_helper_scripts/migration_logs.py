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
    all_volumes = {}
    for volume in tqdm(too_many_list, desc='> 2 Errors:'):
        volume_dict = {'bfid': set(), 'pnfs': set(), 'server_id': database.get_node_id(server),
                       'volume_id': database.get_volume_id(volume)}
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
                        volume_dict['bfid'].add(log_word.strip('found()[]\'\":,(current'))
                    if '/pnfs' in log_word:
                        volume_dict['pnfs'].add(log_word)
                log_details.append((log_file_id, parse_logs.interpret_error_message(message),
                                    message))
            database.insert_log_file_detail(log_details)
        all_volumes[volume] = volume_dict
    return all_volumes


def find_same_copies(bfid):
    """ Run enstore info --find-same-copies bfid """
    try:
        find = subprocess.run(
            [
                '/opt/enstore/Python/bin/python',
                '/opt/enstore/bin/enstore',
                'info',
                '--find-same-copies',
                bfid
            ],
            capture_output=True)
        find = find.stdout.decode()
        print(find)
        exit()
    except FileNotFoundError:
        find = ''
    return find


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
        status = status.stdout.decode().split()[-1]
    except FileNotFoundError:
        status = ''
    return status


def detail_error_messages(all_dict):
    """ receive error list and run enstore commands against volume serials, bfids, and pnfs """
    error_details = []
    bfids = set()
    for volume in all_dict:
        volume_id = database.get_volume_id(volume)
        if not database.volume_id_in_bfid_errors(volume_id):
            for bfid in tqdm(all_dict[volume]['bfid'], desc='Testing BFIDs on ' + volume):
                error_details.append((volume_id, bfid, file_migration_status(bfid) +
                                      find_same_copies(bfid)))
                bfids.add(bfid)
    database.insert_bfid_errors(error_details)
    return bfids


def process(server, quiet=False, rerun=False):
    """ parse command line arguments and run functions """
    archive_count = 0
    rerun_logs = {'msg': 'None'}
    all_errors = {}
    errors = set()
    archive_logs.archive("archive")
    output = see_errors.see_errors()
    logs = parse_logs.parse_logs(output)
    if logs['archive']:
        archive_count = archive_logs.archive("archive-with-errors", sorted(logs['archive']))
    if logs['rerun'] and rerun:
        rerun_logs = build_rerun.rerun(logs['rerun'])
    if logs['too_many']:
        all_errors = too_many_logs(server, sorted(logs['too_many']))
        errors = detail_error_messages(all_errors)

    if not quiet:
        print('Node: ' + server)
        print("archive: " + str(len(logs['archive'])))
        print("rerun: " + str(len(logs['rerun'])))
        print("too many: " + str(len(logs['too_many'])))
        print("bfid errors: " + str(len(errors)))
        print("Archive processed")
        pprint.pprint(archive_count, indent=1)
        print("Rerun processed")
        pprint.pprint(rerun_logs['msg'], indent=1)
        print("Reruns: " + str(len(rerun_logs['rerun'])))
        print('End of line.')
