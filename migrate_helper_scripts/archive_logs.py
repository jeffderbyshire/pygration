#!/home/users/jeffderb/python3/bin/python3

import os
import gzip
import shutil
from .list_logs import *
import sqlite3
import subprocess
import sys
import json
import pprint


LOG_DIRECTORY = "/var/migration/"
LOG_PREFIX = "MigrationLog@"
ARCHIVE_DIR = 'archive/'


def get_year_month(log_name):
    log_name = log_name.replace(LOG_PREFIX, '')
    return "/".join(log_name.split('-')[0:2])


def check_migration_status(unchecked_volumes):
    checked_volumes = []
    for volume in unchecked_volumes:
        status = subprocess.run(['/opt/enstore/Python/bin/python', '/opt/enstore/bin/enstore',
                                'info', '--vol', volume], capture_output=True)
        check = status.stdout.decode().replace("'", '').replace('\n', '')
        if 'migrated' in check:
            checked_volumes.append(volume)
            print(volume + ' migrated')

    sys.exit()

    return checked_volumes, unchecked_volumes


def archive(command="archive", volumes=False):
    logs = get_logs(command, volumes)
    if volumes:
        volumes, original_volumes = check_migration_status(volumes)
    log_total = archived = removed = 0
    if len(logs) > 0:
        for log in logs:
            year_month = get_year_month(log)
            os.makedirs(LOG_DIRECTORY + ARCHIVE_DIR + year_month, exist_ok=True)
            log_file_path = LOG_DIRECTORY + log
            if os.path.exists(log_file_path):
                log_total += 1
                gz_file_path = LOG_DIRECTORY + ARCHIVE_DIR + year_month + '/' + log + '.gz'
                with open(log_file_path, 'rb') as f_in:
                    with gzip.open(gz_file_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                        archived += 1
                if os.path.exists(gz_file_path):
                    with open(log_file_path, 'rb') as fh:
                        first = next(fh).decode().split()
                        volume = first[-1]
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
                    removed += 1
                    conn.close()

    else:
        return {'logs found': logs}

    return {'log count': log_total, 'archived': archived, 'removed': removed}


if __name__ == '__main__':
    archive()
