#!/home/users/jeffderb/python3/bin/python3

import migrate_helper_scripts.list_logs as list_logs
import os
import gzip
import shutil


LOG_DIRECTORY = "/var/migration/"
LOG_PREFIX = "MigrationLog@"
ARCHIVE_DIR = 'archive/'


def get_year_month(log_name):
    log_name = log_name.replace(LOG_PREFIX, '')
    return "/".join(log_name.split('-')[0:2])


def archive(command="archive", volumes=False):
    logs = list_logs.get_logs(command, volumes)
    log_total = archived = removed = 0
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
                os.remove(log_file_path)
                removed += 1

    return {'log count': log_total, 'archived': archived, 'removed': removed}


if __name__ == '__main__':
    archive()
