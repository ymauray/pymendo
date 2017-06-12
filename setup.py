"""PyMendo : a tool to manipulate Jamendo's API"""

# Always prefer setuptools over distutils
from codecs import open
from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='PyMendo',

    version='1.0.0.dev1',

    description='Get tracks from Jamendo using the JSON API.',
    long_description=long_description,

    url='https://github.com/euterpiaradio/pymendo',

    author='Euterpia Radio',
    author_email='info@euterpiaradio.ch',

    license='CC-BY-NC-SA 4.0',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Podcast publishers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7'
    ],

    keywords='audio podcast jamendo',

    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    entry_points={
        'console_scripts': [
            'pymendo=pymendo:main',
        ],
    },
    install_requires=['PyYAML', 'lxml', 'peewee'],
)
