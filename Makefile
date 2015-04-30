
SHELL=/bin/bash

clean:
	rm -rvf ./build
	rm -rf ./dist
	rm -rf ./metrilyx_dataserver.egg-info
	find . -name "*.pyc" -exec rm -rvf '{}' \;


.pydeps:
	which pip || { easy_install pip || exit 1; }


install: .pydeps
	pip install git+https://github.com/metrilyx/opentsdb-pandas.git
	pip install git+https://github.com/metrilyx/metrilyx-dataserver.git
