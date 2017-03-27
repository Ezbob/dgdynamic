
from setuptools import setup

setup(
    name='dgdynamic',
    version='0.5',
    description='Dynamic simulation library for the MØD graph transformation framework',
    url='https://bitbucket.org/Ezben/dgdynamic',
    author='Anders Busch',
    author_email='andersbusch@gmail.com',
    license='MIT',
    packages=['dgDynamic'],
    install_requires=[
        'scipy>=0.18.1',
        'numpy>=1.11.2',
        'sympy>=1.0',
        'matplotlib>=1.5.2'
    ],
    zip_safe=False
)

