===================
Metrilyx Dataserver
===================
Data analysis and delivery server. 


Requirements
------------

**System**

- Atleast 1GB of memory
- 2 or more cores/cpus

**Packages**

+--------------------+-------------------+
| RHEL               | Ubuntu/Debian     |
+====================+===================+
| atlas-devel        | libatlas-dev      |
+--------------------+-------------------+
| blas-devel         | libblas-dev       |
+--------------------+-------------------+
| gcc-c++            | g++               |
+--------------------+-------------------+
| gcc                | gcc               |
+--------------------+-------------------+
| gcc-gfortran       | gfortran          |
+--------------------+-------------------+
| libffi-devel       | libffi-dev        |
+--------------------+-------------------+
| libuuid            | uuid              |
+--------------------+-------------------+
| make               | make              |
+--------------------+-------------------+
| openssl-devel      | libssl-dev        |
+--------------------+-------------------+
| python-devel       | python-dev        |
+--------------------+-------------------+
| python-setuptools  | python-setuptools |
+--------------------+-------------------+

**Python**

* python >= 2.7
* pip >= 6.1.1



Installation
------------

    * pip install git+https://github.com/metrilyx/metrilyx-dataserver.git --process-dependency-links --trusted-host github.com
