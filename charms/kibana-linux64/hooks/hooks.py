#!/usr/bin/env python

import sys

from charmhelpers.contrib.ansible import apply_playbook
from charmhelpers.contrib.python.packages import pip_install
from charmhelpers.core.hookenv import (
    Hooks,
    is_relation_made,
    status_set,
    open_port,
    UnregisteredHookError,
    log as juju_log,
    config
)
from charmhelpers.core.host import service_running
from charmhelpers.fetch import apt_install
from charmhelpers.contrib.charmsupport import nrpe


required_aps = ['build-essential', 'libssl-dev', 'libffi-dev', 'python-dev']
required_pip_packages = ["Ansible==2.1.4.0", "markupsafe"]

service_name = 'kibana'
msg_install_prereqs = 'Installing Ansible pre-reqs'
msg_install_ansible = 'Installing Ansible'
msg_install_service = 'Installing ' + service_name
msg_config_changed = 'Making configuration changes'
msg_missing_es_rel = 'Missing Elasticsearch Relationship'
msg_service_running = 'Unit is ready'
msg_service_stopped = service_name + ' is stopped'
msg_service_failed_to_start = service_name + ' failed to start'

status_maintenance = 'maintenance'
status_blocked = 'blocked'
status_active = 'active'


playbook = 'playbooks/site.yaml'

hooks = Hooks()


@hooks.hook('install', 'upgrade-charm')
def install2():
    """
    Install a custom version of ansible for our charm.
    Because of the hack required to install python with xenial
    our install script is called install2, need to call the ansible playbook
    using the install tag.
    """

    status_set(status_maintenance, msg_install_prereqs)
    apt_install(required_aps)

    status_set(status_maintenance, msg_install_ansible)
    pip_install(required_pip_packages, fatal=True)

    status_set(status_maintenance, msg_install_service)
    apply_playbook(playbook, tags=['install'])


@hooks.hook('config-changed', 'rest-relation-changed')
def config_changed():
    """
    Only run the config_changed ansible playbook tags if elasticsearch
    is present in the bundle
    """
    if is_relation_made("rest"):
        status_set(status_maintenance, msg_config_changed)
        apply_playbook(playbook, tags=['config_changed'])
    else:
        status_set(status_blocked, msg_missing_es_rel)

    update_nrpe_config()
    open_port(config('kibana_ssl_port'), protocol='TCP')


@hooks.hook('nrpe-external-master-relation-joined',
            'nrpe-external-master-relation-changed')
def update_nrpe_config():
    hostname = nrpe.get_nagios_hostname()
    current_unit = nrpe.get_nagios_unit_name()
    services = [service_name]
    nrpe_setup = nrpe.NRPE(hostname=hostname)
    nrpe.add_init_service_checks(nrpe_setup, services, current_unit)
    nrpe_setup.write()


@hooks.hook('start')
def start():
    """
    Special process for the start action so that after the playbook is run
    we can update the status in juju
    """
    if is_relation_made("rest"):
        apply_playbook(playbook, tags=['start'])
        if service_running(service_name):
            status_set(status_active, msg_service_running)
        else:
            status_set(status_maintenance, msg_service_failed_to_start)
    else:
        status_set(status_blocked, msg_missing_es_rel)


@hooks.hook('update-status')
def update_status():
    if is_relation_made("rest"):
        if service_running(service_name):
            status_set(status_active, msg_service_running)
        else:
            status_set(status_maintenance, msg_service_stopped)
    else:
        status_set(status_blocked, msg_missing_es_rel)


@hooks.hook('stop')
def stop():
    apply_playbook(playbook, tags=['stop'])


if __name__ == "__main__":
    try:
        hooks.execute(sys.argv)
    except UnregisteredHookError as e:
        juju_log('Unknown hook {} - skipping.'.format(e))
