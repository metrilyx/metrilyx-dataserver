
SHELL=/bin/bash

clean:
	rm -rvf ./build
	rm -rf ./dist
	rm -rf ./metrilyx_dataserver.egg-info
	find . -name "*.pyc" -exec rm -rvf '{}' \;


.pydeps:
	which pip || { easy_install pip || exit 1; }
	pip install pip --upgrade
	pip install -r requirements.txt

install: .pydeps
	python setup.py install
