from jarvis_cd.shell.exec_node import ExecNode
from jarvis_cd.shell.copy_node import CopyNode
from jarvis_cd.fs.rm_node import RmNode
from jarvis_cd.fs.mkdir_node import MkdirNode
from jarvis_cd.shell.kill_node import KillNode
from jarvis_cd.ssh.openssh.issh_node import InteractiveSSHNode
from jarvis_cd.launcher.launcher import Launcher
from jarvis_cd.ssh.openssh.openssh_config import ToOpenSSHConfig
import os

class Ssh(Launcher):
    def _ProcessConfig(self):
        super()._ProcessConfig()
        self.username = None
        self.port = None
        self.private_key = None
        self.public_key = None
        self.ssh_keys = None

        if self.ssh_info is None:
            return

        self.ssh_keys = {'primary': self.ssh_info}
        if "ssh_keys" in self.config:
            self.ssh_keys.update(self.config['ssh_keys'])

        if 'username' in self.ssh_info:
            self.dst_key_dir = os.path.join('home', self.ssh_info['username'], '.ssh')
        if 'key' in self.ssh_info and 'key_dir' in self.ssh_info:
            self.public_key = self._GetPublicKey(self.ssh_info['key_dir'], self.ssh_info['key'])
            self.private_key = self._GetPublicKey(self.ssh_info['key_dir'], self.ssh_info['key'])
        if 'port' in self.ssh_info:
            self.port = self.ssh_info['port']
        if 'username' in self.ssh_info:
            self.username = self.ssh_info['username']

    def Shell(self, node_id):
        InteractiveSSHNode(self.all_hosts.SelectHosts(node_id)).Run()
    def _ShellArgs(self, parser):
        parser.add_argument('node_id', metavar='id', type=int, help="Node index in hostfile")

    def Exec(self, cmd):
        ExecNode(cmd, hosts=self.all_hosts).Run()
    def _ExecArgs(self, parser):
        parser.add_argument('cmd', metavar='command', type=str, help="The command to distribute")

    def Copy(self, source, destination):
        CopyNode(source, destination, hosts=self.all_hosts).Run()
    def _CopyArgs(self, parser):
        parser.add_argument('source', metavar='path', type=str, help="Source path")
        parser.add_argument('destination', metavar='path', type=str, help="Destination path")

    def Rm(self, path):
        RmNode(path, hosts=self.all_hosts).Run()
    def _RmArgs(self, parser):
        parser.add_argument('path', metavar='path', type=str, help="The path to delete")

    def Mkdir(self, path):
        MkdirNode(path, hosts=self.all_hosts).Run()
    def _MkdirArgs(self, parser):
        parser.add_argument('path', metavar='path', type=str, help="The path to delete")

    def Kill(self, cmd_re):
        KillNode(cmd_re, hosts=self.all_hosts).Run()
    def _KillArgs(self, parser):
        parser.add_argument('cmd_re', metavar='regex', type=str, help='The regex of the process to kill')

    def ModifyConfig(self, rr=True):
        hosts = None
        if rr:
            hosts = self.all_hosts
            CopyNode(self.scaffold_dir, self.scaffold_dir, hosts=hosts).Run()
        ToOpenSSHConfig(register_hosts=self.all_hosts, register_ssh=self.ssh_info, hosts=hosts).Run()
    def _ModifyConfigArgs(self, parser):
        parser.add_argument('-rr', metavar='bool', type=bool, default=True,
                            help='whether or not to modify ssh config on all nodes')

    def Setup(self):
        self._TrustHosts()
        self.ModifyConfig(False)
        self._InstallKeys()
        self._SSHPermissions()


    def _TrustHosts(self):
        # Ensure all self.all_hosts are trusted on this machine
        print("Add all hosts to known_hosts")
        for host in self.all_hosts:
            InteractiveSSHNode(host, self.ssh_info, only_init=True).Run()


    def _InstallKeys(self):
        print("Install SSH keys")
        # Ensure pubkey trusted on all nodes
        for host in self.all_hosts:
            copy_id_cmd = [
                f"ssh-copy-id -f",
                f"-i {self.public_key}" if self.public_key is not None else None,
                f"-p {self.port}" if self.port is not None else None,
                f"{self.username}@{host}" if self.username is not None else host
            ]
            copy_id_cmd = [tok for tok in copy_id_cmd if tok is not None]
            copy_id_cmd = " ".join(copy_id_cmd)
            ExecNode(copy_id_cmd).Run()
        # Create SSH directory on all nodes
        MkdirNode(self.dst_key_dir, hosts=self.all_hosts).Run()

        # Copy all keys:
        for key_entry in self.ssh_keys.keys():
            key_dir, key_name, dst_key_dir = self._GetKeyInfo(key_entry)
            src_pub_key = self._GetPublicKey(key_dir, key_name)
            src_priv_key = self._GetPrivateKey(key_dir, key_name)
            dst_pub_key = self._GetPublicKey(dst_key_dir, key_name)
            dst_priv_key = self._GetPrivateKey(dst_key_dir, key_name)
            CopyNode(src_pub_key, dst_pub_key, hosts=self.all_hosts).Run()
            if os.path.exists(src_priv_key):
                print(f"Copying {src_priv_key} to {dst_priv_key}")
                CopyNode(src_priv_key, dst_priv_key, hosts=self.all_hosts).Run()

    def _SSHPermissionsCmd(self, key_location):
        commands = []
        for key_entry in self.ssh_keys.keys():
            key_dir, key_name, dst_key_dir = self._GetKeyInfo(key_entry)
            if key_location == 'remote':
                key_dir = dst_key_dir
            commands += [
                f'chmod 700 {key_dir}',
                f'chmod 600 {key_dir}/authorized_keys',
                f'chmod 644 {key_dir}/known_hosts',
                f'chmod 600 {key_dir}/config',
                f'chmod 644 {self._GetPublicKey(key_dir, key_name)}',
                f'chmod 600 {self._GetPrivateKey(key_dir, key_name)}'
            ]
        return commands

    def _SSHPermissions(self):
        src_cmd = self._SSHPermissionsCmd('local')
        dst_cmd = self._SSHPermissionsCmd('remote')
        ExecNode(src_cmd, collect_output=False).Run()
        ExecNode(dst_cmd, hosts=self.all_hosts).Run()

    def _GetKeyInfo(self, key_entry):
        key_dir = self.ssh_keys[key_entry]["key_dir"]
        key_name = self.ssh_keys[key_entry]["key"]
        dst_key_dir = self.ssh_keys[key_entry]["dst_key_dir"]
        return key_dir,key_name,dst_key_dir