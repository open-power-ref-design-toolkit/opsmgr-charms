#!/usr/bin/make

build: virtualenv lint

virtualenv: .venv/bin/python
.venv/bin/python:
	@echo "******** One time virtual environment setup ********"
	sudo apt-get install python-virtualenv bzr charm-tools
	virtualenv .venv
	.venv/bin/python -m pip install nose flake8 mock pyyaml

lint:   
	@echo "******** Running lint on python code ********"
	@.venv/bin/python -m flake8 --exclude hooks/charmhelpers hooks
	@echo "******** Running charm proof ********"
	@charm proof

scripts/charm_helpers_sync.py:
	@mkdir scripts
	@wget --directory-prefix scripts \
            https://raw.githubusercontent.com/juju/charm-helpers/master/tools/charm_helpers_sync/charm_helpers_sync.py

sync-charm-helpers: .venv/bin/python scripts/charm_helpers_sync.py
	@echo "******** Syncing charm helpers ********"
	@.venv/bin/python scripts/charm_helpers_sync.py -c charm-helpers.yaml

clean:
	@echo "******** Running clean ********"
	rm -rf .venv
	rm -rf scripts
	find -name *.pyc -delete
