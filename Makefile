all: build

build: *
	python setup.py build

install:
	python setup.py install