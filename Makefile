
clean:
	rm -rvf ./build
	rm -rf ./dist
	rm -rf ./metrilyx_dataserver.egg-info
	find . -name "*.pyc" -exec rm -rvf '{}' \;

install:
	pip install git+https://github.com/metrilyx/opentsdb-pandas.git
	pip install git+https://github.com/metrilyx/metrilyx-dataserver.git
