from jarvis_cd.basic.node import Application
from jarvis_util import *


class GrayScott(Application):
    def _init(self):
        """
        Initialize paths
        """
        self.adios2_xml_path = f'{self.pkg_dir}/config/adios2.xml'
        self.settings_json_path = f'{self.shared_dir}/settings-files.json'

    def _configure_menu(self):
        """
        Create a CLI menu for the configurator method.
        For thorough documentation of these parameters, view:
        https://github.com/scs-lab/jarvis-util/wiki/3.-Argument-Parsing

        :return: List(dict)
        """
        return [
            {
                'name': 'nprocs',
                'msg': 'Number of processes to spawn',
                'type': int,
                'default': 4,
            },
            {
                'name': 'ppn',
                'msg': 'Processes per node',
                'type': int,
                'default': None,
            },
            {
                'name': 'L',
                'msg': 'Grid size of cube',
                'type': int,
                'default': 32,
            },
            {
                'name': 'Du',
                'msg': 'Diffusion rate of substance U',
                'type': float,
                'default': .2,
            },
            {
                'name': 'Dv',
                'msg': 'Diffusion rate of substance V',
                'type': float,
                'default': .1,
            },
            {
                'name': 'F',
                'msg': 'Feed rate of U',
                'type': float,
                'default': .01,
            },
            {
                'name': 'k',
                'msg': 'Kill rate of V',
                'type': float,
                'default': .05,
            },
            {
                'name': 'dt',
                'msg': 'Timestep',
                'type': float,
                'default': 2.0,
            },
            {
                'name': 'steps',
                'msg': 'Total number of steps to simulate',
                'type': int,
                'default': 100,
            },
            {
                'name': 'plotgap',
                'msg': 'Number of steps between output',
                'type': float,
                'default': 10,
            },
            {
                'name': 'noise',
                'msg': 'Amount of noise',
                'type': float,
                'default': .01,
            },
            {
                'name': 'output',
                'msg': 'Absolute path to output data',
                'type': str,
                'default': None,
            },
        ]

    def configure(self, **kwargs):
        """
        Converts the Jarvis configuration to application-specific configuration.
        E.g., OrangeFS produces an orangefs.xml file.

        :param kwargs: Configuration parameters for this node.
        :return: None
        """
        self.update_config(kwargs, rebuild=False)
        if self.config['output'] is None:
            self.config['output'] = os.path.join(os.getcwd(), 'data')
        settings_json = {
            "L": self.config['L'],
            "Du": self.config['Du'],
            "Dv": self.config['Dv'],
            "F": self.config['F'],
            "k": self.config['k'],
            "dt": self.config['dt'],
            "plotgap": self.config['plotgap'],
            "steps": self.config['steps'],
            "noise": self.config['noise'],
            "output": self.config['output'],
            "adios_config": f'{self.shared_dir}/adios2.xml'
        }
        JsonFile(self.settings_json_path).save(settings_json)
        self.copy_template_file(f'{self.pkg_dir}/config/adios2.xml',
                                self.adios2_xml_path)

    def start(self):
        """
        Launch an application. E.g., OrangeFS will launch the servers, clients,
        and metadata services on all necessary nodes.

        :return: None
        """
        Exec(f'gray-scott {self.settings_json_path}',
             MpiExecInfo(nprocs=self.config['nprocs'],
                         ppn=self.config['ppn'],
                         hostfile=self.jarvis.hostfile))

    def stop(self):
        """
        Stop a running application. E.g., OrangeFS will terminate the servers,
        clients, and metadata services.

        :return: None
        """
        pass

    def clean(self):
        """
        Destroy all data for an application. E.g., OrangeFS will delete all
        metadata and data directories in addition to the orangefs.xml file.

        :return: None
        """
        Rm(self.config['output'])
