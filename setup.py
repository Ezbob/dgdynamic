from setuptools import setup
from setuptools.command.install import install
import os
import importlib
import sys
import atexit

if __name__ == '__main__':

    my_name = 'dgDynamic'

    package_dirs = [
        'dgDynamic',
        'dgDynamic/intermediate',
        'dgDynamic/base_converters',
        'dgDynamic/base_converters/ode',
        'dgDynamic/utils',
        'dgDynamic/config',
        'dgDynamic/simulators',
        'dgDynamic/plugins',
        'dgDynamic/plugins/stochastic',
        'dgDynamic/plugins/stochastic/stochkit2',
        'dgDynamic/plugins/stochastic/spim',
        'dgDynamic/plugins/ode',
        'dgDynamic/plugins/ode/matlab',
        'dgDynamic/plugins/ode/scipy'
    ]

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
                        if os.path.isdir(p):
                            for f in os.listdir(p):
                                if f == my_name:
                                    return os.path.join(p, f)
                install_path = find_module_path()
                os.system("tar --extract --file " +
                          os.path.join(install_path, "plugins/stochastic/stochkit2/stochkit.tar.gz"))
                os.system("cd " + os.path.join(install_path, "plugins/stochastic/stochkit2/StochKit/") +
                          "&& ./install.sh")

            atexit.register(_post_install)

            install.run(self)

    setup(
        cmdclass={'install': CustomInstall},
        name='dgdynamic',
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

