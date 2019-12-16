""" build rerun script """

import os
import shutil
from configparser import ConfigParser
from collections import namedtuple
from tqdm import tqdm
import migrate_helper_scripts.check_running as check_running
import migrate_helper_scripts.list_logs as list_logs

CONFIG = ConfigParser()
CONFIG.read('config/config.conf')
RERUN_SCRIPT = CONFIG['Rerun']['rerun_script']
MIGRATION_DIR = CONFIG['Default']['log_dir']
IGNORE = CONFIG['Rerun']['ignore']


def rerun(volumes):
    """ build rerun script and run if disk space free > 60 % and < 2 processes running """
    volumes_dict = {'added': check_running.main(), 'rerun': set(), 'msg': set()}
    if len(volumes_dict['added']) < 2:
        file = open(RERUN_SCRIPT, "w")
        file.write("#!/usr/bin/env bash\n{\ncd /var/migration\nsource ~enstore/.bashrc\n")
        logs = list_logs.get_logs('errors', volumes)
        for log in tqdm(logs, desc='Build Rerun:'):
            command = ''
            ignore = False
            spool_full = False
            with open(MIGRATION_DIR + log, 'rb') as handle:
                first = next(handle).decode().split()
                volume = first[-1]
                for argument in first:
                    if '/data/data' in argument:
                        spool = argument.split('/')
                        try:
                            usage = shutil.disk_usage("/".join(spool[0:3]))
                        except FileNotFoundError:
                            Usage = namedtuple('usage', ['used', 'total'])
                            usage = Usage(1, 1)
                        if usage.used/usage.total > 0.60:
                            volumes_dict['msg'].add("/".join(spool[0:3]) +
                                                    ' is more than 60% full ' + volume)
                            spool_full = True
                            break
                    else:
                        if argument in IGNORE:
                            ignore = True
                            break
                if volume not in volumes_dict['added'] and not ignore and not spool_full:
                    command = "/opt/enstore/Python/bin/python " + " ".join(first[7:])
                    volumes_dict['added'].append(volume)
            if command != '':
                file.write(command + '\n')
                volumes_dict['rerun'].add(command.split()[-1])
        file.write('\nexit\n}\n')
        file.close()
        os.chmod(RERUN_SCRIPT, 0o700)
        os.system('screen -d -m ' + RERUN_SCRIPT)
    else:
        volumes_dict['msg'].add('too many migrate_chimera processes running')

    return volumes_dict


if __name__ == '__main__':
    rerun(False)
