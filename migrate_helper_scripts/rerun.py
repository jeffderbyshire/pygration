import os
import shutil
import migrate_helper_scripts.list_logs as list_logs


RERUN_SCRIPT = '/tmp/migrate.rerun'


def rerun(volumes):
    os.remove(RERUN_SCRIPT)
    file = open(RERUN_SCRIPT, "w")
    header = " \
#!/usr/bin/env bash \
cd /var/migration \
source ~enstore/.bashrc"
    file.write(header)
    logs = list_logs.get_logs('errors', volumes)
    for log in logs:
        print(log)


if __name__ == '__main__':
    rerun(False)
