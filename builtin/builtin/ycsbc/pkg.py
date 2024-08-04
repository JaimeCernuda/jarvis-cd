"""
This module provides classes and methods to launch Redis.
Redis cluster is used if the hostfile has many hosts
"""
from jarvis_cd.basic.pkg import Application
from jarvis_util import *


class Ycsbc(Application):
    """
    This class provides methods to launch the Ior application.
    """
    def _init(self):
        """
        Initialize paths
        """
        pass

    def _configure_menu(self):
        """
        Create a CLI menu for the configurator method.
        For thorough documentation of these parameters, view:
        https://github.com/scs-lab/jarvis-util/wiki/3.-Argument-Parsing

        :return: List(dict)
        """
        return [
            {
                'name': 'db_name',
                'msg': 'The DB to test',
                'type': str,
                'default': 'rocksdb',
                'choices': ['hermes', 'rocksdb', 'leveldb'],
                'args': [],
            },
            {
                'name': 'workload',
                'msg': 'The workload to use',
                'type': str,
                'default': 'a',
                'choices': ['a', 'b', 'c', 'd', 'e', 'f'],
                'args': [],
            },
            {
                'name': 'status',
                'msg': 'Whether or not to print statuses every 10 sec',
                'type': bool,
                'default': True,
                'args': [],
            },
        ]

    def _configure(self, **kwargs):
        """
        Converts the Jarvis configuration to application-specific configuration.
        E.g., OrangeFS produces an orangefs.xml file.

        :param kwargs: Configuration parameters for this pkg.
        :return: None
        """
        pass

    def start(self):
        """
        Launch an application. E.g., OrangeFS will launch the servers, clients,
        and metadata services on all necessary pkgs.

        :return: None
        """
        root = self.env['YCSBC_ROOT']
        db_name = self.config["db_name"]
        workload = f'workload{self.config["workload"]}'
        props = f'{root}/{db_name}/{db_name}.properties'
        if not os.path.exists(props):
            props_arg = ''
        else:
            props_arg = f'-P {props}'
        cmd = [
            'ycsb -run',
            f'-db {db_name}',
            f'-P {root}/workloads/{workload}',
            props_arg,
            f'-s' if self.config['status'] else ''
        ]
        cmd = ' '.join(cmd)
        print(cmd)
        Exec(cmd,
             LocalExecInfo(env=self.mod_env,
                           hostfile=self.jarvis.hostfile,
                           do_dbg=self.config['do_dbg'],
                           dbg_port=self.config['dbg_port']))

    def stop(self):
        """
        Stop a running application. E.g., OrangeFS will terminate the servers,
        clients, and metadata services.

        :return: None
        """
        Kill('redis-server',
             PsshExecInfo(env=self.env,
                          hostfile=self.jarvis.hostfile))

    def clean(self):
        """
        Destroy all data for an application. E.g., OrangeFS will delete all
        metadata and data directories in addition to the orangefs.xml file.

        :return: None
        """
        Rm(self.config['out'] + '*',
           PsshExecInfo(env=self.env,
                        hostfile=self.jarvis.hostfile))
