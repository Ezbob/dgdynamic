from setuptools import setup
from setuptools.command.install import install
import os
import sys
import tarfile
import atexit

if __name__ == '__main__':

    package_name = 'dgdynamic'
    excludes = [
        '__pycache__',
        'StochKit'
    ]

    def find_package_dirs(package_dir_path, excludes):
        return [path for path, dirs, files in os.walk(package_dir_path)
                if not any(exclude_name in path for exclude_name in excludes)]

    package_dirs = find_package_dirs(package_name, excludes)

    extras = [
        'default_config.ini',
        'spim.ocaml',
        'stochkit.tar.gz'
    ]

    p_dict_dir = {
        ".".join(p_name.split('/')): p_name
        for p_name in package_dirs
    }

    class CustomInstall(install):
        def run(self):
            def _post_install():
                def find_module_path():
                    for p in sys.path:
                        if os.path.isdir(p) and package_name in os.listdir(p):
                            return os.path.join(p, package_name)
                install_path = find_module_path()
                stochkit2_plugin_path = os.path.join(install_path, "plugins/stochastic/stochkit2/")
                stochkit2_tar_path = os.path.join(stochkit2_plugin_path, "stochkit.tar.gz")
                stochkit2_installer_path = os.path.join(stochkit2_plugin_path, "StochKit")

                os.system("tar xvzf " + stochkit2_tar_path + " -C " + stochkit2_plugin_path)
                os.system("cd " + stochkit2_installer_path + " && ./install.sh")

            atexit.register(_post_install)

            install.run(self)

    setup(
        cmdclass={'install': CustomInstall},
        name=package_name,
        version='0.5.2',
        description='Dynamic simulation library for the MØD graph transformation framework',
        url='https://bitbucket.org/Ezben/dgdynamic',
        author='Anders Busch',
        author_email='andersbusch@gmail.com',
        license='MIT',
        package_dir=p_dict_dir,
        include_package_data=True,
        package_data={'': extras},
        packages=list(p_dict_dir.keys()),
        install_requires=[
            'scipy>=0.18.1',
            'numpy>=1.11.2',
            'sympy>=1.0',
            'matplotlib>=1.5.2'
        ],
        zip_safe=False
    )

