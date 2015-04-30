
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

INSTALL_REQUIRES = [ p.strip() for p in open('requirements.txt').read().split('\n') 
                                            if p != '' and not p.startswith('#') ]

def fileListBuilder(dirPath, regexp='*'):
    matches = []
    for root, dirnames, filenames in os.walk(dirPath):
        for filename in fnmatch.filter(filenames, regexp):
            matches.append(os.path.join(root, filename))
    return matches


#DATA_FILES = [
#    ('/opt/metrilyx/etc/init.d', fileListBuilder('etc/init.d')),
#    ('/opt/metrilyx/bin/',      fileListBuilder('bin')),
#]


setup(
    name='metrilyx-dataserver',
    version=metrilyx.version,
    url='https://github.com/metrilyx/metrilyx-dataserver',
    description=DESCRIPTION,
    long_description=DESCRIPTION,
    author='euforia',
    author_email='euforia@gmail.com',
    license='Apache',
    install_requires=INSTALL_REQUIRES,
    #data_files=DATA_FILES,
    dependency_links=['git+https://github.com/metrilyx/opentsdb-pandas#egg=opentsdb-pandas'],
    packages=find_packages()
)
