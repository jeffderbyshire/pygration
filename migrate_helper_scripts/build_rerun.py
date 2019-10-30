import os
import shutil
from . import check_running

RERUN_SCRIPT = '/tmp/migrate.rerun'
MIGRATION_DIR = '/var/migration/'
IGNORE = ['--scan', '--restore']


def rerun(volumes):
    volumes_added = check_running.main()
    if len(volumes_added) < 2:
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
                for argument in first:
                    if '/data/data' in argument:
                        spool = argument.split('/')
                        total, used, free = shutil.disk_usage("/".join(spool[0:3]))
                    else:
                        total, used, free = shutil.disk_usage("/data/data3")
                if volume not in volumes_added and used/total < 0.60:
                    command = "/opt/enstore/Python/bin/python " + " ".join(first[7:])
                    for keyword in IGNORE:
                        if keyword in command:
                            command = ''
                            break
                    volumes_added.append(volume)
            if command != '':
                file.write(command + '\n')
                volumes_rerun.append(command.split()[-1])
        os.system('screen -d -m ' + RERUN_SCRIPT)
        file.close()
        return len(volumes_rerun)
    else:
        print('too many migrate_chimera processes running')
        return 0


if __name__ == '__main__':
    from migrate_helper_scripts import list_logs
    rerun(False)
else:
    from . import list_logs
