
import os
import sys
import fnmatch
from setuptools import setup, find_packages
#from pprint import pprint
import metrilyx

DESCRIPTION = '''
Metrilyx dataserver is the core to metrilyx and is responsible for analyzing and 
delivering data to the client.
'''

INSTALL_REQUIRES = [ p for p in open('requirements.txt').read().split('\n') 
                                    if p != '' and not p.startswith('#') ]

def fileListBuilder(dirPath, regexp='*'):
    matches = []
    for root, dirnames, filenames in os.walk(dirPath):
        for filename in fnmatch.filter(filenames, regexp):
            matches.append(os.path.join(root, filename))
    return matches

def recursiveFileListBuilder(dirPath, prefix):
    mine = {}
    for root, dirnames, filenames in os.walk('www'):
        if not mine.has_key(root):
            mine[root] = []

        for filename in fnmatch.filter(filenames, '[!.]*'):
            mine[root].append(filename)

    out = []
    for k, values in mine.items():
        out.append((prefix+k, [ k+'/'+val for val in values ]))
    return out

DATA_FILES = [
    ('/etc/init.d', fileListBuilder('etc/init.d')),
    ('/usr/local/sbin/', fileListBuilder('bin')),
]


setup(
    name='metrilyx-dataserver',
    version=metrilyx.version,
    url='https://github.com/metrilyx/metrilyx-dataserver',
    description=DESCRIPTION,
    long_description=DESCRIPTION,
    author='euforia',
    author_email='euforia@gmail.com',
    license='Apache',
    #setup_requires=SETUP_REQUIRES,
    install_requires=INSTALL_REQUIRES,
    data_files=DATA_FILES,
    packages=find_packages()
)
