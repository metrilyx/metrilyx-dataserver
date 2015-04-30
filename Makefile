
SHELL=/bin/bash

clean:
	rm -rvf ./build
	rm -rf ./dist
	rm -rf ./metrilyx_dataserver.egg-info
	find . -name "*.pyc" -exec rm -rvf '{}' \;


.pydeps:
	which pip || { easy_install pip || exit 1; }
	#pip install pip --upgrade
	#pip install -v numpy
	#pip install -v pandas
	pip install -v git+https://github.com/metrilyx/opentsdb-pandas.git

install: .pydeps
	python setup.py install
	cp -a bin /opt/metrilyx/
	cp -a etc /opt/metrilyx/