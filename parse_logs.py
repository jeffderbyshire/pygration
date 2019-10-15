import pprint
import sys
import collections
import glob

LOG_DIRECTORY = '/var/migration/'


def get_date_time(log_file):
    date_time = log_file.split("MigrationLog@")[1].split("#")[0].split(".")
    date = date_time[0]
    time = date_time[1]
    return [date, time]


def is_vol_archived(volume_serial):
    found = glob.glob(LOG_DIRECTORY + 'archive/*/*/*' + volume_serial + '.gz')
    if len(found) > 0:
        return True

    return False


def rerun_error_message(message):
    rerun_messages = [
        "TOO MANY RETRIES",
        "TIMEOUT",
        "COPYING_TO_DISK"
    ]

    for rerun in rerun_messages:
        if rerun in message:
            return True

    return False


def interpret_error_message(message):
    matched_knowns = []
    known_messages = [
        "[Errno 2] No such file or directory: PNFS ID not found:",
        "Destination directory writes 19 copies; only 19 libraries specified for",
        "are inconsistent on bfid ... ERROR",
        "[1] metadata",
        "[2] metadata",
        "COPYING_TO_TAPE failed to copy",
        "SWAPPING_METADATA no file record found",
        "TOO MANY RETRIES",
        "skipping volume metadata update since not all files have been scanned",
        "FINAL_SCAN FINAL_SCAN_VOLUME",
        "has not been swapped",
        "is not a migration destination volume",
        "is not a migration bfid",
        "FINAL_SCAN LOG_HISTORY_CLOSED did not set",
        "COPYING_TO_DISK trying to migrate file",
        "GET_INPUT_TARGETS can not find bfid of file-family-width",
        "READ_0 COPYING_TO_DISK failed to copy",
        "Error after transferring 0 bytes in 1 files",
        "TIMEDOUT"
    ]
    if message == "":
        return False
    for known in known_messages:
        if known in message:
            matched_knowns.append(known)

    if len(matched_knowns) > 0:
        return " ".join(matched_knowns)

    return "Unknown Error " + message


def parse_logs(server, logs):
    no_error = "No Error Found in Log File"
    archive_logs_list = []
    rerun_logs_list = []
    too_many_errors_list = []
    volume_serial_list = []
    message_list = []
    parsed_log_dict = {}
    archive_flag = {}
    for line in logs:
        if len(line) > 10:
            volume_serial, log_file_name, log_error_message = line.split(" ---- ")
            # print(split_line)
            # if len(x) > 0:
            date_time = get_date_time(log_file_name)
            date_str = date_time[0]
            time_str = date_time[1]
            log_error_message_condensed = interpret_error_message(log_error_message)
            if log_error_message_condensed is False:
                log_error_message_condensed = no_error
                archive_flag[volume_serial] = True
            if volume_serial not in volume_serial_list:
                volume_serial_list.append(volume_serial)
            message_list.append([volume_serial, date_str, time_str, log_error_message_condensed])

    vol_error = []
    for vol_ser, date_str, time_str, msg in message_list:
        vol_error.append([vol_ser, msg])

    counter = collections.Counter()
    for vol, error in vol_error:
        counter[vol, error] += 1
    # leave for debugging pprint.pprint(counter, indent=1)
    """ 1. Archive Logs if No errors found """
    for vol, msg in list(counter):
        vol_archived = is_vol_archived(vol)
        if no_error == msg or vol_archived:
            # print(vol)
            archive_logs_list.append(vol)
            for vol_2, msg_2 in list(counter):
                if vol == vol_2:
                    # print(vol_2, msg_2)
                    key = (vol_2, msg_2)
                    del counter[key]

    # leave for debugging pprint.pprint(counter, indent=1)
    for vol, msg in list(counter):
        if rerun_error_message(msg):
            rerun_logs_list.append(vol)
        else:
            if counter[(vol, msg)] < 3:
                # rerun_vol_ser(vol)
                rerun_logs_list.append(vol)
            else:
                # too many errors to rerun
                too_many_errors_list.append(vol)

    archive_logs_list = list(set(archive_logs_list))
    rerun_logs_list = list(set(rerun_logs_list))
    too_many_errors_list = list(set(too_many_errors_list))
    return sorted(archive_logs_list), sorted(rerun_logs_list), sorted(too_many_errors_list), counter
