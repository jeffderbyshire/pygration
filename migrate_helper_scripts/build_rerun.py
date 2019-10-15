import os
import shutil
from . import check_running

RERUN_SCRIPT = '/tmp/migrate.rerun'
MIGRATION_DIR = '/var/migration/'
IGNORE = ['--scan', '--restore']


def rerun(volumes):
    run_ok = True
    volumes_added = check_running.main()
    if len(volumes_added) > 1:
        run_ok = False
    volumes_rerun = []
    os.chmod(RERUN_SCRIPT, 0o700)
    file = open(RERUN_SCRIPT, "w")
    header = "#!/usr/bin/env bash\ncd /var/migration\nsource ~enstore/.bashrc\n"
    file.write(header)
    logs = list_logs.get_logs('errors', volumes)
    for log in logs:
        command = ''
        file_name = MIGRATION_DIR + log
        with open(file_name, 'rb') as fh:
            first = next(fh).decode().split()
            volume = first[-1]
            if volume not in volumes_added:
                command = "/opt/enstore/Python/bin/python " + " ".join(first[7:])
                for keyword in IGNORE:
                    if keyword in command:
                        command = ''
                        break
                volumes_added.append(volume)
        if command != '':
            file.write(command + '\n')
            volumes_rerun.append(command.split()[-1])
    if run_ok:
        os.system('screen -d -m ' + RERUN_SCRIPT)
    else:
        print('too many migrate_chimera processes running')
    file.close()
    return len(volumes_rerun)


if __name__ == '__main__':
    from migrate_helper_scripts import list_logs
    rerun(False)
else:
    from . import list_logs
