===================
Metrilyx Dataserver
===================
Data analysis and delivery server. 


Requirements
------------

+---------------+---------------+
| RHEL          | Ubuntu/Debian |
+===============+===============+
| atlas-devel   | libatlas-dev  |
+---------------+---------------+
| blas-devel    | libblas-dev   |
+---------------+---------------+
| gcc-c++       | g++           |
+---------------+---------------+
| gcc           | gcc           |
+---------------+---------------+
| gcc-gfortran  | gfortran      |
+---------------+---------------+
| libffi-devel  | libffi-dev    |
+---------------+---------------+
| libuuid       | uuid          |
+---------------+---------------+
| make          | make          |
+---------------+---------------+
| openssl-devel | libssl-dev    |
+---------------+---------------+
| python-devel  | python-dev    |
+---------------+---------------+


Installation
------------

Install the opentsdb pandas library like so:

    * pip install git+https://github.com/metrilyx/opentsdb-pandas.git

Once installed continue to install the dataserver:

    * pip install git+https://github.com/metrilyx/metrilyx-dataserver.git --process-dependency-links --trusted-host github.com
