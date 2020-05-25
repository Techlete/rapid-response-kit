VIRTUALENV = $(shell which virtualenv)

ifeq ($(strip $(VIRTUALENV)),)
  VIRTUALENV = /usr/local/python/bin/virtualenv
endif


install: venv
	pip install -r requirements.txt
	python install.py
	python setup.py install

develop: venv
	pip install -r requirements.txt
	pip install -r tests/requirements.txt
	python install.py
	python setup.py develop

venv:
	$(VIRTUALENV) venv

serve: venv
	python rapid_response_kit/app.py

debug: venv
	python rapid_response_kit/app.py --debug

test: venv
	nosetests tests

coverage: venv
	nosetests --with-coverage --cover-package=rapid_response_kit

htmlcov: venv
	nosetests --with-coverage --cover-html --cover-package=rapid_response_kit
	open cover/index.html


flake: venv
	flake8 --ignore=F401 rapid_response_kit

clean:
	rm -rf *.pyc
	rm -rf cover/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf build/

uninstall: clean
	rm -rf venv
