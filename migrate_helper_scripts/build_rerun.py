""" build rerun script """

import os
import socket
import subprocess
import logging
import shutil
from configparser import ConfigParser
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


def logger(log_type="info", message="N/A"):
    """ logger instance for rerun """
    database.insert_log(socket.gethostname(), "rerun", log_type, message)


def write_run_file(commands, script_file, job):
    """ write rerun file with dictionary of commands[volume] = command """
    file = open(script_file, "w")
    file.write("#!/usr/bin/env bash\n{\ncd /var/migration\nsource /home/enstore/.bashrc\n")
    file.write("# %s\n" % job)
    for volume, command in commands.items():
        file.write("/opt/enstore/Python/bin/python %s %s\n" % (command, volume))
    file.write('\nexit\n}\n')
    file.close()
    os.chmod(script_file, 0o700)
    logger("info", "%s file with %s volumes" % (job, str(len(commands.keys()))))


def run_file(script, start_run=False, job="Rerun"):
    """ run rerun file if # migration processes < 2 running """
    if len(check_running.main()[0]) > 1:
        start_run = False
    if start_run:
        run_result = subprocess.run(
            [
                '/usr/bin/screen',
                '-d',
                '-m',
                script
            ],
            capture_output=True,
            env=include.ENSTORE_ENV
        )
        logging.info(run_result.stdout.decode())

    logging.info("%s enabled: %s and %s processes running",
                 job,
                 str(start_run),
                 str(len(check_running.main()[0])))
    logger("info", "Run %s %s and %s processes running" %
           (job, str(start_run), str(len(check_running.main()[0]))))


def check_pnfs(volume):
    """ check mtab to see which pnfs is mount and check volume family and compare """
    volume_result = subprocess.run(
        [
            '/opt/enstore/Python/bin/python',
            '/opt/enstore/bin/enstore',
            'info',
            '--vol',
            volume
        ],
        capture_output=True,
        timeout=20,
        env=include.ENSTORE_ENV
    )
    is_family_cms = bool("'volume_family': 'cms." in volume_result.stdout.decode())
    with open('/etc/mtab') as file:
        is_pnfs_cms = bool('cmsdcatapedb' in file.read())

    if (is_family_cms and is_pnfs_cms) or (not is_family_cms and not is_pnfs_cms):
        return True

    logging.info("%s is cms %s and pnfs is cms %s", volume, is_family_cms, is_pnfs_cms)
    return False


def disk_usage_ok(command_list):
    """ search for spool directory and check disk usage < 60% """
    for argument in command_list:
        if '/data/data' in argument:
            usage = shutil.disk_usage(argument)
            if usage.used / usage.total < 0.60:
                return True

    logging.info("Disk usage > 60%")
    logger("info", "Disk usage > 60%")
    return False


def ignore_not_found(command_list):
    """ search for ignore rerun commands such as scan or restore """
    found = False
    for argument in command_list:
        if argument not in IGNORE:
            found = True

    return found


def is_volume_running(volume):
    """ check if volume is not in database get running """
    running = database.get_running()
    for volume_running in running:
        logging.debug("volume %s vs running %s", str(volume), str(volume_running))
        if volume in str(volume_running):
            return True
    return False


def rerun(volumes, start_rerun=False, quiet=False):
    """ build rerun script and run if disk space free > 60 % and < 2 processes running """
    volumes_dict = {'added': check_running.main()[0], 'rerun': set(), 'msg': set()}
    commands_dict = {}
    for log in tqdm(list_logs.get_logs('errors', volumes), disable=quiet, desc='Build Rerun:'):
        logging.debug("%s", log)
        rerun_dict = {
            'first': list(),
            'volume': ''}
        with open(MIGRATION_DIR + log, 'rb') as handle:
            rerun_dict['first'] = next(handle).decode().split()
            rerun_dict['volume'] = rerun_dict['first'][-1]
            if rerun_dict['volume'] not in commands_dict.keys() \
                    and ignore_not_found(rerun_dict['first'][7:-1]) \
                    and not is_volume_running(rerun_dict['volume']):
                if check_pnfs(rerun_dict['volume']):
                    if disk_usage_ok(rerun_dict['first'][7:-1]):
                        commands_dict[rerun_dict['volume']] = \
                            " ".join(rerun_dict['first'][7:-1])
                        volumes_dict['rerun'].add(rerun_dict['volume'])
                else:
                    logger("pnfs mismatch", "/opt/enstore/Python/bin/python " +
                           " ".join(rerun_dict['first'][7:-1]))
    write_run_file(commands_dict, RERUN_SCRIPT, "Rerun")
    run_file(RERUN_SCRIPT, start_rerun)

    return volumes_dict


if __name__ == '__main__':
    rerun(False)
