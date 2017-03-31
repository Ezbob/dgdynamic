from setuptools import setup
from setuptools.command.install import install
import os
import sys
import atexit

if __name__ == '__main__':

    package_name = 'dgdynamic'
    excludes = [
        '__pycache__',
        'StochKit'
    ]
    extras = [
        'default_config.ini',
        'spim.ocaml',
        'stochkit.tar.gz'
    ]

    def find_package_dirs(package_dir_path, excludes):
        return [path for path, dirs, files in os.walk(package_dir_path)
                if not any(exclude_name in path for exclude_name in excludes)]

    def get_requirements():
        with open('requirements.txt', mode="r") as file:
            return list(map(str.strip, file))

    package_dirs = find_package_dirs(package_name, excludes)

    internal_python_paths = {
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
        package_dir=internal_python_paths,
        include_package_data=True,
        package_data={'': extras},
        packages=list(internal_python_paths.keys()),
        install_requires=get_requirements(),
        zip_safe=False
    )

