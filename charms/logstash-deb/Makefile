#!/usr/bin/make

build: virtualenv lint ansible-lint test

virtualenv: .venv/bin/python
.venv/bin/python:
	@echo "******** One time virtual environment setup ********"
	sudo apt-get install python-virtualenv bzr charm-tools
	virtualenv .venv
	.venv/bin/python -m pip install nose flake8 mock pyyaml 'ansible-lint>=2.0.3,<=2.3.6'

lint:   
	@echo "******** Running lint on python code ********"
	@.venv/bin/python -m flake8 --exclude hooks/charmhelpers hooks unit_tests
	@echo "******** Running charm proof ********"
	@charm proof

ansible-lint:
	@echo "******** Running lint on ansible code ********"
	@bash -c "find ./playbooks -name '*.yml' | xargs .venv/bin/ansible-lint"

test:
	@echo "******** Running unit tests ********"
	@CHARM_DIR=. PYTHONPATH=./hooks .venv/bin/nosetests --nologcapture unit_tests

scripts/charm_helpers_sync.py:
	@mkdir scripts
	@bzr cat lp:charm-helpers/tools/charm_helpers_sync/charm_helpers_sync.py \
		> scripts/charm_helpers_sync.py

sync-charm-helpers: scripts/charm_helpers_sync.py
	@echo "******** Syncing charm helpers ********"
	@.venv/bin/python scripts/charm_helpers_sync.py -c charm-helpers.yaml

clean:
	@echo "******** Running clean ********"
	rm -rf .venv
	rm -rf scripts
	find -name *.pyc -delete
