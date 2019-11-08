import os
import argparse
import configparser
import paramiko


paramiko.util.log_to_file('wang_ssh.log')
parser = argparse.ArgumentParser("wang SSH 功能列表...")


class AcceptPolicy(paramiko.MissingHostKeyPolicy):
    def miss_host_key(self, client, hostname, key):
        return


class HostConfig:
    """配置操作相关"""
    def __init__(self, host='', pwd='', user='', port=''):
        self.host = host
        self.pwd = pwd
        self.user = user
        self.port = port
        self.base_dir = os.getcwd()

    def add_config(self):
        "添加配置文件"
        config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        section = 'host_info'
        config.add_section(section)
        config.set(section,'HOST', self.host)
        config.set(section,'PWD', self.pwd)
        config.set(section,'USER', self.user)
        config.set(section,'PORT', self.port)
        config_path = os.path.join(self.base_dir, 'common.ini')  # 配置文件路径
        with open(config_path, 'a') as f:
            config.write(f)

    def read_config(self):
        """读配置文件"""
        config = configparser.ConfigParser()
        config_path = os.path.join(self.base_dir, 'common.ini')  # 配置文件路径
        config.read(config_path)
        host = config['host_info']['HOST']
        pwd = config['host_info']['PWD']
        user = config['host_info']['USER']
        return(host, user, pwd)


class WangSSH:
    def __init__(self, host='', user='', password=''):
        self.host_config = HostConfig()
        self.host, self.user, self.password  = self.host_config.read_config()
        self.client = self.connect(self.host, self.user, self.password)

    def close(self):
        self.client.close()

    def connect(self, host, user, password):
        """连接服务器"""
        client = ''
        try:
            print('连接服务器....')
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(AcceptPolicy())        
            client.connect(host, username=user, password=password)
            print(client)
        except Exception as e:
            print()
        return(client)

    def connect_many(self, hosts):
        """连接多个服务器"""
        for host in hosts:
            client = host + 'client'
            client = self.connect(host, 'root', 'king123')
            print(client, "连接成功")
            self.close()
        # return(client)

    def send_cmd(self, cmd):
        """发送给命令，取得返回值"""
        try:
                
            stdin, stdout, stderr = self.client.exec_command(cmd)
            print(stdout, stderr)
            return stdout
        except paramiko.SSHException as e:
            print(e)

    def upload_file(self, local_file_path, remote_file_path):
        """put local file to remote server"""
        ret = {'status': 0, 'msg': 'ok'}
        try:
            if self.client:
                ftp_client = self.client.open_sftp()
                ftp_client.put(local_file_path, remote_file_path)
                ftp_client.close()
            else:
                ret['status'] = 1
                ret['msg'] = 'error'
        except Exception as e:
            print(e)
            ret['status'] = 1
            ret['msg'] = 'error'
        return ret


    def download_file(self, remote_file_path, local_file_path):
        """get remote server  to local file """
        ret = {'status': 0, 'msg': 'ok'}
        try:
            if self.client:
                ftp_client = self.client.open_sftp()
                ftp_client.get(remote_file_path, local_file_path)
                ftp_client.close()
            else:
                ret['status'] = 1
                ret['msg'] = 'error'
        except Exception as e:
            print(e)
            ret['status'] = 1
            ret['msg'] = 'error'
        return ret


def main():

    parser.add_argument(dest='filenames', nargs='*', help='文件列表，第一个表示本地文件，第二个表示远程文件')

    # upload
    parser.add_argument('-u', '--upload', dest='upload', action='store_true', help='上传文件，需要追加文件名')
    parser.add_argument('-d', '--download', dest='download', action='store_true', help='下载文件，需要追加文件名')
    parser.add_argument('-c', '--console', dest='console', action='store_true', help='shell命令交互界面')
    parser.add_argument('-s', '--login', dest='login', action='append', metavar='login', help='添加ip连接和登陆服务器，多个参数连接多个')
    args = parser.parse_args()


    if args.upload:
        if args.filenames:
            client = WangSSH()
            if client:
                local_file_path = args.filenames[0]
                remote_file_path = args.filenames[1]
                stdout = client.upload_file(local_file_path, remote_file_path)
                print(stdout)
                client.close
        else:
            parser.print_help()
    elif args.download:
        if args.filenames:
            client = WangSSH()
            if client:
                remote_file_path = args.filenames[0]
                local_file_path = args.filenames[1]
                stdout = client.download_file(remote_file_path, local_file_path)
                print(stdout)
                client.close
        else:
            parser.print_help()
    elif args.console:
        client = WangSSH().client
        if client:
            while True:
                print('[q]-quit!')
                cmd = input('shell >>')
                if cmd == 'q':
                    break
                stdin, stdout, stderr = client.exec_command(cmd)
                print(stdout.read().decode())
            client.close        
    elif args.login:
        client = WangSSH()
        client.connect_many(args.filenames)
    else:
        parser.print_help()
        return
if __name__ == '__main__':
    main()