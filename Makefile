SHELL=/bin/bash

NAME = metrilyx-dataserver
VERSION = $(shell cat VERSION)
DESCRIPTION = Metrilyx data delivery server
BUILD_DIR_BASE = ./build
BUILD_DIR = ${BUILD_DIR_BASE}/${NAME}

.clean:
	rm -rf ${BUILD_DIR_BASE}
	rm -rf ./dist
	rm -rf ./metrilyx_dataserver.egg-info
	rm -rf ./_trial_temp
	find . -name "*.pyc" -exec rm -rvf '{}' \;

.install:
	pip install . --process-dependency-links --trusted-host github.com

.rpm: .clean
	[ -d ${BUILD_DIR_BASE}/el ] || mkdir -p ${BUILD_DIR_BASE}/el
	cd ${BUILD_DIR_BASE}/el &&  fpm -s python -t rpm ../../setup.py

.deb: .clean
	[ -d ${BUILD_DIR_BASE}/ubuntu ] || mkdir -p ${BUILD_DIR_BASE}/ubuntu
	cd ${BUILD_DIR_BASE}/ubuntu &&  fpm -s python -t deb ../../setup.py


all: .clean .install