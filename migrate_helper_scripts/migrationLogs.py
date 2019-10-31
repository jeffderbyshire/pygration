import parse_logs
import pprint
import syncBashScripts
import sqlite3
from . import archive_logs
from . import list_logs
from . import build_rerun
from . import error_check
from . import see_errors
from . import error_report
from . import progress_bar as pb


def too_many_logs(server, too_many_list):
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
    pb.print_progress_bar(0, len(too_many_list), prefix='> 2 Errors:', suffix='Complete', length=50)
    i = 0
    for volume in too_many_list:
        i += 1
        # select first then insert
        cursor.execute("SELECT rowid FROM volumes WHERE volume = ?", (volume, ))
        volume_id = cursor.fetchone()
        if volume_id is None:
            cursor.execute("INSERT INTO volumes VALUES(?)", (volume, ))
            volume_id = cursor.lastrowid
            conn.commit()
        else:
            volume_id = volume_id[0]
        error_logs = list_logs.get_logs("errors", [volume])
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
        pb.print_progress_bar(i, len(too_many_list), prefix='> 2 Errors:', suffix='Complete',
                              length=50)

    conn.close()


def process(server, item, volume=False, quiet=False):

    if item == "check":
        output = error_check.main()

    elif item == "rerun":
        if volume:
            command = "bash /root/migrate_helper_scripts/rerunMigrationErrors.sh " + volume
        else:
            command = "bash /root/migrate_helper_scripts/rerunMigrationErrors.sh"

    elif item == "archive" or item == "archive_with_errors":
        output = archive_logs.archive(item, volume)

    elif item == "fix_archives":
        command = "bash /root/migrate_helper_scripts/fixArchives.sh"

    elif item == "group_errors":
        command = "bash /root/migrate_helper_scripts/groupErrorsByExperiments.sh"

    elif item == "see_errors":
        archive_logs.archive("archive")
        output = see_errors.see_errors()
        archive, rerun, too_many, counter = parse_logs.parse_logs(server, output)
        print("archive: " + str(len(archive)))
        print("rerun: " + str(len(rerun)))
        print("too many: " + str(len(too_many)))
        if len(archive) > 0:
            # pprint.pprint(archive)
            archive_count = archive_logs.archive("archive-with-errors", sorted(archive))
            # pprint.pprint(list_logs.get_logs('archive-with-errors', sorted(archive)))
            print("Archive")
            pprint.pprint(archive_count, indent=1)
        if len(rerun) > 0:
            rerun_logs = build_rerun.rerun(rerun)
            print("Rerun")
            pprint.pprint(rerun_logs, indent=1)
        if len(too_many) > 0:
            # print("More than 2 errors:")
            # pprint.pprint(too_many, indent=1)
            # pprint.pprint(counter, indent=1)
            too_many_logs(server, sorted(too_many))

    elif item == "report":
        output = error_report.push()

    else:
        command = "echo 'do nothing'"

    if not quiet:
        print(server)
        print(item)
        if item != "see_errors":
            pprint.pprint(output, indent=4)
