from setuptools import setup

if __name__ == '__main__':

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

    setup(
        name='dgdynamic',
        version='0.5',
        description='Dynamic simulation library for the MØD graph transformation framework',
        url='https://bitbucket.org/Ezben/dgdynamic',
        author='Anders Busch',
        author_email='andersbusch@gmail.com',
        license='MIT',
        package_dir=p_dict_dir,
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

