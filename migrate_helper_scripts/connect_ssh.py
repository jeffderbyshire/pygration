""" connect via ssh and kerberos """

import pprint
from paramiko import client
from paramiko import ssh_gss

ssh = client.SSHClient()
ssh.set_missing_host_key_policy(client.AutoAddPolicy())
ssh.connect(hostname='fdm1801.fnal.gov',
            username='root',
            gss_auth=True)
stdin, stdout, stderr = ssh.exec_command("ps ww", get_pty=True)
stdin.close()
output = []
for line in stdout.readlines():
    output.append(line.strip())
exit_status = stdout.channel.recv_exit_status()
ssh.close()
if exit_status and raise_error:
    raise OSError(exit_status, output)
pprint.pprint(output)
