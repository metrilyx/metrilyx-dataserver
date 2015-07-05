SHELL=/bin/bash

NAME = metrilyx-dataserver
VERSION = $(shell cat VERSION)
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

all: .clean .install
