
FROM centos

RUN yum -y update

RUN yum -y install atlas-devel blas-devel gcc-c++ gcc gcc-gfortran libffi-devel libuuid make openssl-devel python-devel python-setuptools git numpy

RUN which pip || easy_install pip

RUN pip install pip --upgrade

RUN pip install git+https://github.com/metrilyx/metrilyx-dataserver --process-dependency-links --trusted-host github.com