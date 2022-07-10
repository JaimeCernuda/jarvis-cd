from abc import ABC, abstractmethod
from jarvis_cd.enumerations import Color
import inspect

class Node(ABC):
    def __init__(self, print_output=True, collect_output=True, name=None):
        self.print_output = print_output
        self.name = name
        self.collect_output = collect_output
        self.output = [{ "localhost": {
            "stdout": [""],
            "stderr": [""]
        }}]

    def Print(self):
        #For each command
        for host_outputs in self.output:
            #Print all host outputs
            for host,outputs in host_outputs.items():
                for line in outputs['stdout']:
                    print("[INFO] {host} {line}".format(host=host, line=line))
                for line in outputs['stderr']:
                    print(Color.RED + "[ERROR] {host} {line}".format(host=host, line=line)+ Color.END)

    def GetOutput(self):
        return self.output

    @abstractmethod
    def _Run(self):
        pass

    def _ToShellCmd(self):
        node_import = type(self).__module__
        node_params = self.__init__.__code__.co_varnames
        node_vals = [self.__dict__[f'self.{key}'] for key in node_params]
        node_type = type(self).__name__
        param_str = ','.join([f"{key}={val}" for key,val in zip(node_params,node_vals)])
        return f"python3 -c from {node_import} import {node_type}; {node_type}({param_str}).Run()"

    def Run(self):
        self._Run()
        if self.print_output:
            self.Print()
        return self

    def __str__(self):
        return self.name
