import subprocess


def rsync(server, folder):
    command = "rsync -qua --delete "+folder+" root@"+server+":/root/"
    print(command)
    try:
        subprocess.run(
                        ["rsync", "-vua", "--delete", folder, "root@"+server+":/root/"],
                        check=True)
    except subprocess.CalledProcessError as err:
        print('ERROR:', err)

