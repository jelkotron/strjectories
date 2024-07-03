try:
     from setuptools import setup
except ImportError:
     from distutils.core import setup

config = {
     'description': 'Utilities to track and visualize satellites in real time',
     'author': 'Oliver Jelko',
     'author_email': 'ojelko@proton.me',
     'install_requires': ['pytest'],
     'packages': ['satutils'],
     'scripts': [],
     'name': 'satutils'
}

setup(**config)