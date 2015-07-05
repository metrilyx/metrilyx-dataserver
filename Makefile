SHELL=/bin/bash

NAME = metrilyx-dataserver
VERSION = $(shell cat VERSION)
BUILD_DIR_BASE = ./build
BUILD_DIR = ${BUILD_DIR_BASE}/${NAME}

INSTALL_DIR = /opt/metrilyx
PYTHON_LIB_DIR = ${INSTALL_DIR}/lib/python2.7/site-packages

AB_RPM_DEPS = -d python-twisted-core -d python-wsaccel -d 'python-six >= 1.6.1' -d python-txaio
AB_DEB_DEPS = -d python-twisted -d python-wsaccel -d 'python-six >= 1.6.1' -d python-txaio

RPM_DEPS = -d python-autobahn -d python-ujson -d libuuid
DEB_DEPS = -d python-autobahn -d python-ujson -d libuuid1

.clean:
	rm -rf ${BUILD_DIR_BASE}
	rm -rf ./dist
	rm -rf ./metrilyx_dataserver.egg-info
	rm -rf ./_trial_temp
	find . -name "*.pyc" -exec rm -rvf '{}' \;

.install:
	pip install . --process-dependency-links --trusted-host github.com

# python-txaio
.txaio_rpm:
	[ -d ${BUILD_DIR_BASE}/el ] || mkdir -p ${BUILD_DIR_BASE}/el
	cd ${BUILD_DIR_BASE}/el &&  fpm -s python -t rpm --python-install-lib ${PYTHON_LIB_DIR} txaio

.txaio_deb:
	[ -d ${BUILD_DIR_BASE}/ubuntu ] || mkdir -p ${BUILD_DIR_BASE}/ubuntu
	cd ${BUILD_DIR_BASE}/ubuntu &&  fpm -s python -t deb --python-install-lib ${PYTHON_LIB_DIR} txaio

# python-six
.six_rpm:
	[ -d ${BUILD_DIR_BASE}/el ] || mkdir -p ${BUILD_DIR_BASE}/el
	cd ${BUILD_DIR_BASE}/el &&  fpm -s python -t rpm --python-install-lib ${PYTHON_LIB_DIR} six

.six_deb:
	[ -d ${BUILD_DIR_BASE}/ubuntu ] || mkdir -p ${BUILD_DIR_BASE}/ubuntu
	cd ${BUILD_DIR_BASE}/ubuntu &&  fpm -s python -t deb --python-install-lib ${PYTHON_LIB_DIR} six

# python-wsaccel
.wsaccel_rpm:
	[ -d ${BUILD_DIR_BASE}/el ] || mkdir -p ${BUILD_DIR_BASE}/el
	cd ${BUILD_DIR_BASE}/el &&  fpm -s python -t rpm --python-install-lib ${PYTHON_LIB_DIR} wsaccel

.wsaccel_deb:
	[ -d ${BUILD_DIR_BASE}/ubuntu ] || mkdir -p ${BUILD_DIR_BASE}/ubuntu
	cd ${BUILD_DIR_BASE}/ubuntu &&  fpm -s python -t deb --python-install-lib ${PYTHON_LIB_DIR} wsaccel

# python-autobahn
.autobahn_rpm:
	[ -d ${BUILD_DIR_BASE}/el ] || mkdir -p ${BUILD_DIR_BASE}/el
	cd ${BUILD_DIR_BASE}/el &&  fpm -s python -t rpm --no-python-dependencies --python-install-lib ${PYTHON_LIB_DIR} ${AB_RPM_DEPS} autobahn

.autobahn_deb:
	[ -d ${BUILD_DIR_BASE}/ubuntu ] || mkdir -p ${BUILD_DIR_BASE}/ubuntu
	cd ${BUILD_DIR_BASE}/ubuntu &&  fpm -s python -t deb --no-python-dependencies --python-install-lib ${PYTHON_LIB_DIR} ${AB_DEB_DEPS} autobahn

# App
.rpm: .wsaccel_rpm .six_rpm .txaio_rpm .autobahn_rpm
	[ -d ${BUILD_DIR_BASE}/el ] || mkdir -p ${BUILD_DIR_BASE}/el
	cd ${BUILD_DIR_BASE}/el &&  fpm -s python -t rpm --python-install-lib ${PYTHON_LIB_DIR} ${RPM_DEPS} ../../setup.py

.deb: .wsaccel_deb .six_deb .txaio_deb .autobahn_deb
	[ -d ${BUILD_DIR_BASE}/ubuntu ] || mkdir -p ${BUILD_DIR_BASE}/ubuntu
	cd ${BUILD_DIR_BASE}/ubuntu &&  fpm -s python -t deb --python-install-lib ${PYTHON_LIB_DIR} ${DEB_DEPS} ../../setup.py


all: .clean .install
