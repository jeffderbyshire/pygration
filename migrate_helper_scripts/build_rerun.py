""" build rerun script """

import os
import shutil
import migrate_helper_scripts.check_running as check_running
import migrate_helper_scripts.progress_bar as progress_bar


RERUN_SCRIPT = '/tmp/migrate.rerun'
MIGRATION_DIR = '/var/migration/'
IGNORE = ['--scan', '--restore']
DATA3 = '/data/data3'
DATA2 = '/data/data2'
DATA1 = '/data/data1'


def rerun(volumes):
    """ build rerun script and run if disk space free > 60 % and < 2 processes running """
    volumes_added = check_running.main()
    if len(volumes_added) < 2:
        volumes_rerun = []
        msg = []
        file = open(RERUN_SCRIPT, "w")
        header = "#!/usr/bin/env bash\ncd /var/migration\nsource ~enstore/.bashrc\n"
        file.write(header)
        logs = list_logs.get_logs('errors', volumes)
        for i, log in enumerate(logs):
            progress_bar.print_progress_bar(i, len(logs), prefix='Build Rerun:')
            command = ''
            ignore = False
            spool_full = False
            file_name = MIGRATION_DIR + log
            with open(file_name, 'rb') as fh:
                first = next(fh).decode().split()
                volume = first[-1]
                for argument in first:
                    if '/data/data' in argument:
                        spool = argument.split('/')
                        total, used, free = shutil.disk_usage("/".join(spool[0:3]))
                        if used/total > 0.60:
                            msg.append("/".join(spool[0:3]) + ' is more than 60% full ' + volume)
                            spool_full = True
                            break
                    else:
                        if argument in IGNORE:
                            ignore = True
                            break
                if volume not in volumes_added and not ignore and not spool_full:
                    command = "/opt/enstore/Python/bin/python " + " ".join(first[7:])
                    volumes_added.append(volume)
            if command != '':
                file.write(command + '\n')
                volumes_rerun.append(command.split()[-1])
        file.close()
        if len(msg) > 0:
            print(msg)
        os.chmod(RERUN_SCRIPT, 0o700)
        os.system('screen -d -m ' + RERUN_SCRIPT)
        return len(volumes_rerun)
    else:
        print('too many migrate_chimera processes running')
        return 0


if __name__ == '__main__':
    from migrate_helper_scripts import list_logs
    rerun(False)
else:
    from . import list_logs
