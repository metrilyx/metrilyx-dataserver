
SHELL=/bin/bash

clean:
	rm -rvf ./build
	rm -rf ./dist
	rm -rf ./metrilyx_dataserver.egg-info
	rm -rf ./_trial_temp
	find . -name "*.pyc" -exec rm -rvf '{}' \;


.pydeps:
	which pip || easy_install pip


install: .pydeps
	pip install . -v --process-dependency-links --trusted-host github.com
	cp -a bin /opt/metrilyx/
	cp -a etc /opt/metrilyx/

