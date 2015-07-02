#
# metrilyx-dataserver
#
FROM ubuntu

RUN apt-get update -y

RUN apt-get -y install libatlas-dev libblas-dev g++ gcc gfortran libffi-dev uuid make libssl-dev python-dev python-setuptools git python-numpy

RUN which pip || easy_install pip

RUN pip install pip --upgrade

RUN pip install git+https://github.com/metrilyx/metrilyx-dataserver --process-dependency-links --trusted-host github.com
