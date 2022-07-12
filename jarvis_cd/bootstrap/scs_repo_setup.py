from jarvis_cd.installer.git_node import GitNode, GitOps
from jarvis_cd.installer.modify_env_node import ModifyEnvNode, ModifyEnvNodeOps
from jarvis_cd.basic.exec_node import ExecNode
from jarvis_cd.bootstrap.package import Package
import sys,os
import shutil

class SCSRepoSetup(Package):
    def _LocalInstall(self):
        scs_repo_root = self.config['scs_repo']['path']
        GitNode(**self.config['scs_repo'], method=GitOps.CLONE, collect_output=False, print_output=True, print_fancy=False).Run()
        ExecNode(f'spack repo add {scs_repo_root}').Run()
        ModifyEnvNode(self.jarvis_env, f"export SCS_REPO", ModifyEnvNodeOps.REMOVE).Run()
        ModifyEnvNode(self.jarvis_env, f"export SCS_REPO={scs_repo_root}", ModifyEnvNodeOps.APPEND).Run()

    def _LocalUpdate(self):
        scs_repo_root = os.environ['SCS_REPO']
        GitNode(**self.config['scs_repo'], method=GitOps.UPDATE, collect_output=False, print_output=True, print_fancy=False).Run()

    def _LocalUninstall(self):
        scs_repo_root = os.environ['SCS_REPO']
        shutil.rmtree(scs_repo_root)
        ModifyEnvNode(self.jarvis_env, f"export SCS_REPO", ModifyEnvNodeOps.REMOVE).Run()