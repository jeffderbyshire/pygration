""" Process logs

Main command line is --process see_errors
Parses logs for volume serials to archive, rerun, and too many errors
store too many errors in sqlite db
"""
import pprint
import sqlite3
from tqdm import tqdm
import migrate_helper_scripts.archive_logs as archive_logs
import migrate_helper_scripts.parse_logs as parse_logs
import migrate_helper_scripts.list_logs as list_logs
import migrate_helper_scripts.build_rerun as build_rerun
import migrate_helper_scripts.error_check as error_check
import migrate_helper_scripts.see_errors as see_errors


def too_many_logs(server, too_many_list):
    """ Connect to sqlite db and insert server, volume serial, and log file details"""
    conn = sqlite3.connect('/home/users/jeffderb/db/migration.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT rowid FROM servers WHERE server=?", (server, ))
    server_id = cursor.fetchone()
    if server_id is None:
        cursor.execute("INSERT INTO servers VALUES (?)", (server, ))
        server_id = cursor.lastrowid
        conn.commit()
    else:
        server_id = server_id[0]
    for volume in tqdm(too_many_list, desc='> 2 Errors:'):
        # select first then insert
        cursor.execute("SELECT rowid FROM volumes WHERE volume = ?", (volume, ))
        volume_id = cursor.fetchone()
        if volume_id is None:
            cursor.execute("INSERT INTO volumes VALUES(?)", (volume, ))
            volume_id = cursor.lastrowid
            conn.commit()
        else:
            volume_id = volume_id[0]
        error_logs = list_logs.get_logs("errors", {volume})
        for log_file in error_logs:
            date = log_file.split("MigrationLog@")[1].split("#")[0].split(".")[0]
            cursor.execute("INSERT OR IGNORE INTO log_files VALUES(?, ?, ?, ?)",
                           (server_id, volume_id, log_file, date))
            log_file_id = cursor.lastrowid
            conn.commit()
            error_messages = see_errors.error_messages('/var/migration/' + log_file)
            log_details = []
            for message in error_messages:
                log_details.append((log_file_id, parse_logs.interpret_error_message(message),
                                    message))

            cursor.executemany("INSERT OR IGNORE INTO log_file_detail VALUES(?, ?, ?)", log_details)
            conn.commit()

    conn.close()


def process(server, item, volume=False, quiet=False):
    """ parse command line arguments and run functions """
    if item == "check":
        output = error_check.main()

    elif item in {'archive', 'archive_with_errors'}:
        output = archive_logs.archive(item, volume)

    elif item == "see_errors":
        archive_logs.archive("archive")
        output = see_errors.see_errors()
        logs = parse_logs.parse_logs(output)
        print("archive: " + str(len(logs['archive'])))
        print("rerun: " + str(len(logs['rerun'])))
        print("too many: " + str(len(logs['too_many'])))
        if logs['archive']:
            # pprint.pprint(archive)
            archive_count = archive_logs.archive("archive-with-errors", sorted(logs['archive']))
            # pprint.pprint(list_logs.get_logs('archive-with-errors', sorted(archive)))
            print("Archive")
            pprint.pprint(archive_count, indent=1)
        if logs['rerun']:
            rerun_logs = build_rerun.rerun(logs['rerun'])
            print("Rerun")
            pprint.pprint(rerun_logs, indent=1)
        if logs['too_many']:
            # print("More than 2 errors:")
            # pprint.pprint(too_many, indent=1)
            # pprint.pprint(counter, indent=1)
            too_many_logs(server, sorted(logs['too_many']))

    if not quiet:
        print(server)
        print(item)
        if item != "see_errors":
            pprint.pprint(output, indent=4)
