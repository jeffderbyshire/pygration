import os
import shutil

RERUN_SCRIPT = '/tmp/migrate.rerun'
MIGRATION_DIR = '/var/migration/'
IGNORE = ['--scan', '--restore']


def rerun(volumes):
    command = ''
    os.remove(RERUN_SCRIPT)
    file = open(RERUN_SCRIPT, "w")
    header = "#!/usr/bin/env bash\ncd /var/migration\nsource ~enstore/.bashrc\n"
    file.write(header)
    logs = list_logs.get_logs('errors', volumes)
    for log in logs:
        file_name = MIGRATION_DIR + log
        with open(file_name, 'rb') as fh:
            first = next(fh).decode().split()
            command = " ".join(first[7:])
            for keyword in IGNORE:
                if keyword in command:
                    command = ''
                    break
        if command != '':
            file.write(command + '\n')

    file.close()

if __name__ == '__main__':
    from migrate_helper_scripts import list_logs
    rerun(False)
else:
    from . import list_logs
