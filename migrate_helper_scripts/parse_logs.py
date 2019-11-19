""" parse logs """

import collections
import glob
import subprocess
from migrate_helper_scripts import progress_bar as pb


LOG_DIRECTORY = '/var/migration/'


def get_date_time(log_file):
    """ get date and time from log file name """
    date_time_list = log_file.split("MigrationLog@")[1].split("#")[0].split(".")
    date_time = {'date': date_time_list[0], 'time': date_time_list[1]}
    return date_time


def is_vol_archived(volume_serial):
    """ check archives to see if volume serial is in archive as non-error migrated log file """
    found = glob.glob(LOG_DIRECTORY + 'archive/*/*/*' + volume_serial + '.gz')
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
        "COPYING_TO_DISK",
        "COPYING_TO_TAPE",
        "Error after transferring 0 bytes in 1 files",
        "TIMEOUT",
        "TOO MANY RETRIES",
    ]

    for rerun in rerun_messages:
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
        "are inconsistent on bfid ... ERROR",
        "COPYING_TO_DISK trying to migrate file",
        "COPYING_TO_TAPE failed to copy",
        "COPYING_TO_TAPE cleanup lists are not empty",
        "Destination directory writes 19 copies; only 19 libraries specified for",
        "does not exist in db",
        "Error after transferring 0 bytes in 1 files",
        "FINAL_SCAN FINAL_SCAN_VOLUME",
        "FINAL_SCAN LOG_HISTORY_CLOSED did not set",
        "GET_INPUT_TARGETS can not find bfid of file-family-width",
        "has not been swapped",
        "is NOTALLOWED",
        "is not a migration bfid",
        "is not a migration destination volume",
        "MainThread MIGRATING_VOLUME do not set",
        "READ_0 COPYING_TO_DISK failed to copy",
        "skipping volume metadata update since not all files have been scanned",
        "SWAPPING_METADATA no file record found",
        "TIMEDOUT",
        "to migrated due to previous error",
        "TOO MANY RETRIES",
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
        capture_output=True)
    check = status.stdout.decode()
    return bool('migrated' in check)


def parse_logs(logs):
    """ Parse logs """
    no_error = "No Error Found in Log File"
    logs_list = {'archive': set([]), 'rerun': set([]), 'too_many': set([])}
    counter = collections.Counter()

    for i, line in enumerate(logs):
        pb.print_progress_bar(i, len(logs), prefix='Read Errors:')
        if len(line) > 10:
            volume_serial, log_error_message = line.split(" ---- ")
            # print(split_line)
            # if len(x) > 0:
            log_error_message_snippet = interpret_error_message(log_error_message)
            if log_error_message_snippet is False:
                log_error_message_snippet = no_error
            counter[volume_serial, log_error_message_snippet] += 1
    # leave for debugging pprint.pprint(counter, indent=1)
    # 1. Archive Logs if No errors found
    for i, [vol, msg] in enumerate(list(counter)):
        pb.print_progress_bar(i, len(list(counter)), prefix='Archive Check:')
        if check_migration_status(vol) or is_vol_archived(vol) or archive_error_message(msg):
            # print(vol)
            logs_list['archive'].add(vol)
            for vol_2, msg_2 in list(counter):
                if vol == vol_2:
                    # print(vol_2, msg_2)
                    key = (vol_2, msg_2)
                    del counter[key]
    # leave for debugging pprint.pprint(counter, indent=1)
    for i, [vol, msg] in enumerate(list(counter)):
        pb.print_progress_bar(i, len(list(counter)), prefix='Rerun Check:')
        if rerun_error_message(msg):
            logs_list['rerun'].add(vol)
        else:
            if counter[(vol, msg)] < 3:
                # rerun_vol_ser(vol)
                logs_list['rerun'].add(vol)
            else:
                # too many errors to rerun
                logs_list['too_many'].add(vol)
    return logs_list