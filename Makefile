all: build html 

html: doc
	python setup.py html

build: *
	python setup.py build

install:
	python setup.py install

clean:
	python setup.py clean

test:
	python setup.py test
