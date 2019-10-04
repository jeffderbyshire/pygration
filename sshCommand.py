import subprocess


def sshcmd(host, command, user="root", stdin=None):
    """ Runs ssh command via subprocess.  Assuming .ssh/config is configured.
    Args:
        host: target host to send the command to
        command: command to run on the host
        user: (optional) user to use to login to host
        stdin: (optional) override sys.stdin
    Returns:
        subprocess.CompletedProcess object
    """
    if ".fnal.gov" not in host:
        host = host + ".fnal.gov"
    where = "%s" % host if user is None else "%s@%s" %(user, host)
    result = subprocess.run(["ssh", where, command],
                            shell=False,
                            stdin=stdin,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            check=False)
    return result

