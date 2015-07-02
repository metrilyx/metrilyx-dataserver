
SHELL=/bin/bash

NAME = metrilyx-dataserver
VERSION = $(shell cat VERSION)
BUILD_DIR_BASE = ./build
BUILD_DIR = ${BUILD_DIR_BASE}/${NAME}

.clean:
	rm -rvf ./build
	rm -rf ./dist
	rm -rf ./metrilyx_dataserver.egg-info
	rm -rf ./_trial_temp
	find . -name "*.pyc" -exec rm -rvf '{}' \;


.pydeps:
	which pip || easy_install pip


.install: .pydeps
	pip install . -v --process-dependency-links --trusted-host github.com

.rpm:
	cd ${BUILD_DIR_BASE} &&  fpm -s python -t rpm -n ${NAME} --version ${VERSION} ${NAME}

.deb:
	cd ${BUILD_DIR_BASE} &&  fpm -s python -t deb -n ${NAME} --version ${VERSION} ${NAME}


all: .clean .install