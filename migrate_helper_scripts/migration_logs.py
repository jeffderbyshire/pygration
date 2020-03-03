""" Process logs

Main command line is --process see_errors
Parses logs for volume serials to archive, rerun, and too many errors
store too many errors in sqlite db
"""
import logging
import subprocess
from configparser import ConfigParser
from tqdm import tqdm
import migrate_helper_scripts.archive_logs as archive_logs
import migrate_helper_scripts.parse_logs as parse_logs
import migrate_helper_scripts.list_logs as list_logs
import migrate_helper_scripts.build_rerun as build_rerun
import migrate_helper_scripts.see_errors as see_errors
import migrate_helper_scripts.database_schema as database
import migrate_helper_scripts.enstore_env as include

CONFIG = ConfigParser()
CONFIG.read('config/config.conf')
LOG_PREFIX = CONFIG['Default']['log_prefix']
LOG_DIR = CONFIG['Default']['log_dir']
BFID_CLEANUP = 'found()[]\'\":,(current\'{}'


def too_many_logs(server, too_many_list, quiet=False):
    """ Connect to sqlite db and insert server, volume serial, and log file details"""
    all_volumes = {}
    for volume in tqdm(too_many_list, disable=quiet, desc='> 2 Errors:'):
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
                        volume_dict['bfid'].add(log_word.strip(BFID_CLEANUP))
                    if '/pnfs' in log_word:
                        volume_dict['pnfs'].add(log_word)
                log_details.append((log_file_id, parse_logs.interpret_error_message(message),
                                    message))
            database.insert_log_file_detail(log_details)
        all_volumes[volume] = volume_dict
    return all_volumes


def find_same_file(bfid):
    """ Run enstore info --find-same-copies bfid """
    same_file_result = ''
    same_file_result = subprocess.run(
        [
            '/opt/enstore/Python/bin/python',
            '/opt/enstore/bin/enstore',
            'info',
            '--find-same-file',
            bfid
        ],
        timeout=30,
        capture_output=True,
        env=include.ENSTORE_ENV
    )
    same_file_result = same_file_result.stdout.decode()

    return same_file_result


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
            timeout=5,
            capture_output=True,
            env=include.ENSTORE_ENV
        )
        try:
            status = status.stdout.decode().split()[-1]
        except IndexError:
            status = False
    except subprocess.TimeoutExpired:
        status = 'timeout status check'

    return status


def detail_error_messages(all_dict, quiet=False):
    """ receive error list and run enstore commands against volume serials, bfids, and pnfs """
    bfids = set()
    for volume in all_dict:
        if bool(all_dict[volume]['bfid']):
            volume_id = database.get_volume_id(volume)
            if not database.volume_id_in_bfid_errors(volume_id):
                for bfid in tqdm(all_dict[volume]['bfid'], disable=quiet,
                                 desc='Testing BFIDs on ' + volume):
                    bfid = bfid.strip(BFID_CLEANUP)
                    if not database.does_bfid_exist(bfid):
                        database.insert_bfid_errors(volume_id, bfid, '')
                        bfids.add(bfid)
    return bfids


def process(server, quiet=False, rerun=False):
    """ parse command line arguments and run functions """
    archive_count = 0
    rerun_logs = {'msg': 'None', 'rerun': set()}
    all_errors = {}
    errors = set()
    archive_logs.archive("archive")
    output = see_errors.see_errors()
    logs = parse_logs.parse_logs(output)
    if logs['archive']:
        archive_count = archive_logs.archive("archive-with-errors", sorted(logs['archive']), quiet)
    if logs['rerun']:
        rerun_logs = build_rerun.rerun(logs['rerun'], rerun, quiet)
    if logs['too_many']:
        all_errors = too_many_logs(server, sorted(logs['too_many']), quiet)
        errors = detail_error_messages(all_errors, quiet)

    if not quiet:
        logging.info("Node: %s", server)
        logging.info("archive logs %s", len(logs['archive']))
        logging.info("rerun %s", len(logs['rerun']))
        logging.info("foobar %s", len(logs['too_many']))
        logging.info("new bfid errors %s", len(errors))
        logging.info("archived with errors %s", archive_count)
        logging.info("Rerun %s volumes", len(rerun_logs['rerun']))
