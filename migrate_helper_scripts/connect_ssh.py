""" connect via ssh and kerberos """

import pprint
from paramiko import client


def connect_ssh(node, command):
    """ connect to node and run command.  Return output """
    ssh = client.SSHClient()
    ssh.set_missing_host_key_policy(client.AutoAddPolicy())
    ssh.connect(hostname=node,
                username='root',
                gss_auth=True)
    stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
    stdin.close()
    output = {"stdout": list(stdout), "stderr": list(stderr)}
    exit_status = stdout.channel.recv_exit_status()
    ssh.close()
    if exit_status:
        raise OSError(exit_status, output)
    return output


if __name__ == '__main__':
    pprint.pprint(connect_ssh('fdm1801.fnal.gov', 'df -h'))
