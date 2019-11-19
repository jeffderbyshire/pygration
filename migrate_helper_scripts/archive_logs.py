""" archive logs """
import gzip
import shutil
import sqlite3
import collections
import os
import migrate_helper_scripts.list_logs as list_logs
import migrate_helper_scripts.progress_bar as print_progress_bar


LOG_DIRECTORY = "/var/migration/"
LOG_PREFIX = "MigrationLog@"
ARCHIVE_DIR = 'archive/'


def get_year_month(log_name):
    """ parse year and month from log file name """
    log_name = log_name.replace(LOG_PREFIX, '')
    return "/".join(log_name.split('-')[0:2])


def archive(command="archive", volumes=False):
    """ main archive function
    make path with LOG Directory / year / month
    gzip log file and mv to archive path and delete log file
    search and delete volume serial from sqlite error log db """
    logs = list_logs.get_logs(command, volumes)
    totals = collections.Counter()
    if logs:
        for i, log in enumerate(logs):
            print_progress_bar.print_progress_bar(i, len(logs), prefix='Archive Logs:')
            year_month = get_year_month(log)
            os.makedirs(LOG_DIRECTORY + ARCHIVE_DIR + year_month, exist_ok=True)
            log_file_path = LOG_DIRECTORY + log
            if os.path.exists(log_file_path):
                totals['log count'] += 1
                gz_file_path = LOG_DIRECTORY + ARCHIVE_DIR + year_month + '/' + log + '.gz'
                with open(log_file_path, 'rb') as f_in:
                    with gzip.open(gz_file_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                        totals['archived'] += 1
                if os.path.exists(gz_file_path):
                    with open(log_file_path, 'rb') as handle:
                        volume = next(handle).decode().split()[-1]
                    conn = sqlite3.connect('/home/users/jeffderb/db/migration.sqlite')
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM log_file_detail WHERE log_file_id IN ( "
                                   "SELECT a.log_file_id FROM log_file_detail a "
                                   "INNER JOIN log_files b ON b.rowid = a.log_file_id  "
                                   "INNER JOIN volumes c ON b.volume_id = c.rowid "
                                   "WHERE c.volume=?)", (volume, ))
                    cursor.execute("DELETE FROM log_files WHERE volume_id IN ( "
                                   "SELECT a.volume_id FROM log_files a "
                                   "INNER JOIN volumes b ON a.volume_id = b.rowid "
                                   "WHERE b.volume=?)", (volume, ))
                    cursor.execute("DELETE FROM volumes "
                                   "WHERE volume=?", (volume, ))
                    conn.commit()
                    os.remove(log_file_path)
                    totals['removed'] += 1
                    conn.close()

    else:
        return {'logs found': logs}

    return totals


if __name__ == '__main__':
    archive()
