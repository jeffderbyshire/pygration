""" parse logs """

import collections
import glob
import logging
import subprocess
from configparser import ConfigParser
from tqdm import tqdm
import migrate_helper_scripts.database_schema as database
import migrate_helper_scripts.enstore_env as include


CONFIG = ConfigParser()
CONFIG.read('config/config.conf')
LOG_PREFIX = CONFIG['Default']['log_prefix']
LOG_DIRECTORY = CONFIG['Default']['log_dir']
ARCHIVE_DIR = CONFIG['Archive']['archive_dir']


def get_date_time(log_file):
    """ get date and time from log file name """
    date_time_list = log_file.split(LOG_PREFIX)[1].split("#")[0].split(".")
    date_time = {'date': date_time_list[0], 'time': date_time_list[1]}
    return date_time


def is_vol_archived(volume_serial):
    """ check archives to see if volume serial is in archive as non-error migrated log file """
    found = glob.glob(LOG_DIRECTORY + ARCHIVE_DIR + '*/*/*' + volume_serial + '.gz')
    if found:
        return True

    return False


def archive_error_message(message):
    """ Return True if special archive messages are found """
    archive_messages = [
        "does not exist in db",
        "is NOTALLOWED",
    ]

    for archive in archive_messages:
        if archive in message:
            return True

    return False


def rerun_error_message(message):
    """ Return True if special rerun error messages are found """
    rerun_messages = [
        "Error after transferring 0 bytes in 1 files",
        'Noticed the local file inode changed',
        'pg.ProgrammingError',
        "TIMEOUT",
        "TIMEDOUT",
        "TOO MANY RETRIES",
        "Too many open files",
    ]

    for rerun in rerun_messages:
        logging.info("check rerun condition %s message is %s", rerun, message)
        if rerun in message:
            return True

    return False


def interpret_error_message(message):
    """ Look for Unknown errors and return snippets of known errors """
    matched_knowns = []
    known_messages = [
        "[1] metadata",
        "[2] metadata",
        "[Errno 2] No such file or directory: PNFS ID not found:",
        "already duplicated to",
        "are inconsistent on bfid ... ERROR",
        "COPYING_TO_DISK cleanup lists are not empty",
        "COPYING_TO_DISK failed to copy",
        "COPYING_TO_DISK trying to migrate file",
        "COPYING_TO_TAPE cleanup lists are not empty",
        "COPYING_TO_TAPE failed to copy",
        "COPYING_TO_TAPE size check mismatch",
        'COPYING_TO_TAPE Tried to write to invalid directory entry',
        "Destination directory writes 19 copies; only 19 libraries specified for",
        "does not exist in db",
        "Error after transferring 0 bytes in 1 files",
        "failed due to Can not move package file in pnfs from",
        "FILE WAS MODIFIED",
        "FINAL_SCAN FINAL_SCAN_VOLUME",
        "FINAL_SCAN LOG_HISTORY_CLOSED did not set",
        "GET_INPUT_TARGETS can not find bfid of file-family-width",
        "has not been swapped",
        'insert or update on table "migration" violates foreign key constraint "$2"',
        "is NOTALLOWED",
        "is not a migration bfid",
        "is not a migration destination volume",
        "MainThread MIGRATING_VOLUME do not set",
        "MIGRATING_VOLUME do not set",
        "Noticed the local file inode changed",
        "pg.ProgrammingError",
        "READ_0 COPYING_TO_DISK failed to copy",
        "skipping volume metadata update since not all files have been scanned",
        "SWAPPING_METADATA no file record found",
        "SWAP_METADATA",
        "TIMEDOUT",
        "to migrated due to previous error",
        "TOO MANY RETRIES",
        "Too many open files",
    ]
    if message == "":
        return False
    for known in known_messages:
        if known in message:
            matched_knowns.append(known)

    if matched_knowns:
        return " ".join(matched_knowns)

    return "Unknown Error " + message


def check_migration_status(volume):
    """ Run enstore command and Return True if 'migrated' in result """
    status = subprocess.run(
        [
            '/opt/enstore/Python/bin/python',
            '/opt/enstore/bin/enstore',
            'info',
            '--check',
            volume
        ],
        capture_output=True,
        env=include.ENSTORE_ENV,
        timeout=20
    )
    check = status.stdout.decode()
    if 'migrated' in check:
        database.insert_migrated(volume)
        return True

    return False


def parse_logs(logs):
    """ Parse logs """
    no_error = "No Error Found in Log File"
    logs_list = {'archive': set([]), 'rerun': set([]), 'too_many': set([])}
    counter = collections.Counter()

    for line in tqdm(logs, desc='Reading Errors:'):
        if len(line) > 10:
            volume_serial, log_error_message = line.split(" ---- ")
            logging.info("%s", volume_serial)
            # print(split_line)
            # if len(x) > 0:
            log_error_message_snippet = interpret_error_message(log_error_message)
            if log_error_message_snippet is False:
                log_error_message_snippet = no_error
            counter[volume_serial, log_error_message_snippet] += 1
    # leave for debugging pprint.pprint(counter, indent=1)
    # 1. Archive Logs if No errors found
    for [vol, msg] in tqdm(list(counter), desc='Archive Check:'):
        if database.volume_is_migrated(vol) \
                or is_vol_archived(vol) \
                or archive_error_message(msg) \
                or check_migration_status(vol):
            logs_list['archive'].add(vol)
            for vol_2, msg_2 in list(counter):
                if vol == vol_2:
                    # print(vol_2, msg_2)
                    key = (vol_2, msg_2)
                    del counter[key]
    # leave for debugging pprint.pprint(counter, indent=1)
    for [vol, msg] in tqdm(list(counter), desc='Rerun Check:'):
        logging.info("checking volume %s message is %s", vol, msg)
        if rerun_error_message(msg):
            logging.info("volume %s rerun for %s", vol, msg)
            logs_list['rerun'].add(vol)
        else:
            logs_list['too_many'].add(vol)

    logging.info("%s", logs_list)
    return logs_list
