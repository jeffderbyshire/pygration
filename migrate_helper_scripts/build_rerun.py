""" build rerun script """

import os
import subprocess
import shutil
from configparser import ConfigParser
from collections import namedtuple
from tqdm import tqdm
import migrate_helper_scripts.check_running as check_running
import migrate_helper_scripts.list_logs as list_logs
import migrate_helper_scripts.database_schema as database
import migrate_helper_scripts.enstore_env as include

CONFIG = ConfigParser()
CONFIG.read('config/config.conf')
RERUN_SCRIPT = CONFIG['Rerun']['rerun_script']
MIGRATION_DIR = CONFIG['Default']['log_dir']
IGNORE = CONFIG['Rerun']['ignore']


def check_pnfs(volume):
    """ check mtab to see which pnfs is mount and check volume family and compare """
    is_family_cms = False
    is_pnfs_cms = False
    volume_result = subprocess.run(
        [
            '/opt/enstore/Python/bin/python',
            '/opt/enstore/bin/enstore',
            'info',
            '--vol',
            volume
        ],
        capture_output=True,
        timeout=10,
        env=include.ENSTORE_ENV
    )
    result_dict = volume_result.stdout.decode()
    print(result_dict['volume_family'])
    for line in volume_result.stdout.decode():
        if 'volume_family' in line:
            is_family_cms = bool('cms.' in line)
    with open('/etc/mtab') as file:
        is_pnfs_cms = bool('cmsdcatapedb' in file.read())

    if (is_family_cms and is_pnfs_cms) or (not is_family_cms and not is_pnfs_cms):
        return True

    return False


def rerun(volumes, start_rerun=False):
    """ build rerun script and run if disk space free > 60 % and < 2 processes running """
    volumes_dict = {'added': check_running.main(), 'rerun': set(), 'msg': set()}
    if len(volumes_dict['added']) < 2:
        file = open(RERUN_SCRIPT, "w")
        file.write("#!/usr/bin/env bash\n{\ncd /var/migration\nsource ~enstore/.bashrc\n")
        for log in tqdm(list_logs.get_logs('errors', volumes), desc='Build Rerun:'):
            rerun_dict = {
                'command': '',
                'first': list(),
                'ignore': False,
                'spool': list(),
                'spool_full': False,
                'volume': ''}
            with open(MIGRATION_DIR + log, 'rb') as handle:
                rerun_dict['first'] = next(handle).decode().split()
                rerun_dict['volume'] = rerun_dict['first'][-1]
                if check_pnfs(rerun_dict['volume']):
                    for argument in rerun_dict['first']:
                        if '/data/data' in argument:
                            rerun_dict['spool'] = argument.split('/')
                            try:
                                usage = shutil.disk_usage("/".join(rerun_dict['spool'][0:3]))
                            except FileNotFoundError:
                                Usage = namedtuple('usage', ['used', 'total'])
                                usage = Usage(1, 1)
                            if usage.used / usage.total > 0.60:
                                volumes_dict['msg'].add("/".join(rerun_dict['spool'][0:3]) +
                                                        ' is more than 60% full ' +
                                                        rerun_dict['volume'])
                                rerun_dict['spool_full'] = True
                                break
                        else:
                            if argument in IGNORE:
                                rerun_dict['ignore'] = True
                                break
                    if rerun_dict['volume'] not in database.get_running() \
                            and not rerun_dict['ignore'] and not rerun_dict['spool_full']:
                        rerun_dict['command'] = "/opt/enstore/Python/bin/python " + \
                                                rerun_dict['first'][7] + \
                                                " ".join(rerun_dict['first'][8:])
                        volumes_dict['added'].append(rerun_dict['volume'])
            if rerun_dict['command'] != '':
                file.write(rerun_dict['command'] + '\n')
                volumes_dict['rerun'].add(rerun_dict['command'].split()[-1])
        file.write('\nexit\n}\n')
        file.close()
        os.chmod(RERUN_SCRIPT, 0o700)
        if start_rerun:
            os.system('screen -d -m ' + RERUN_SCRIPT)
    else:
        volumes_dict['msg'].add('too many migrate_chimera processes running')

    return volumes_dict


if __name__ == '__main__':
    rerun(False)
