import os
import shutil

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
    return logs


if __name__ == '__main__':
    from migrate_helper_scripts import list_logs
    rerun(False)
else:
    from . import list_logs
