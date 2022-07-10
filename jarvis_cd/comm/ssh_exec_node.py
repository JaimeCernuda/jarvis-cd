from pssh.clients import ParallelSSHClient
import sys
from jarvis_cd.basic.parallel_node import ParallelNode
from jarvis_cd.exception import Error, ErrorCode

sys.stderr = sys.__stderr__

class SSHExecNode(ParallelNode):
    def __init__(self, cmds, **kwargs):

        """
        cmds is assumed to be a list of shell commands
        Do not use SSHExecNode directly, use ExecNode instead
        """
        super().__init__(**kwargs)

        #Make sure commands are a list
        if isinstance(cmds, list):
            self.cmds=cmds
        elif isinstance(cmds, str):
            self.cmds=[cmds]
        else:
            raise Error(ErrorCode.INVALID_TYPE).format("SSHExecNode cmds", type(cmds))

    def _exec_ssh(self, cmd):
        client = ParallelSSHClient(self.hosts, user=self.username, pkey=self.pkey, password=self.password, port=self.port)
        output = client.run_command(cmd, sudo=self.sudo, use_pty=not self.exec_async)
        nice_output = dict()
        for host_output in output:
            host = host_output.host
            nice_output[host]={
                'stdout':[],
                'stderr':[]
            }
            nice_output[host]['stdout'] = list(host_output.stdout)
            nice_output[host]['stderr'] = list(host_output.stderr)
            nice_output[host]['stdout'].insert(0, cmd)
        return [nice_output]

    def _Run(self):
        if not self.do_ssh:
            return
        if self.sudo:
            self.cmds.insert(0, f"source /home/{self.username}/.bashrc")
        cmd = " ; ".join(self.cmds)
        self.output = self._exec_ssh(cmd)
        return self

    def __str__(self):
        return "SSHExecNode {}".format(self.name)
