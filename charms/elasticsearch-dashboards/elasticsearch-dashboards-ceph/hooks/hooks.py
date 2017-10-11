#!/usr/bin/env python

import os
import sys
from subprocess import call
from retrying import retry

from charmhelpers.core.hookenv import (
    Hooks,
    log as juju_log,
    relation_get,
    status_set,
    unit_get,
    UnregisteredHookError
)

from charmhelpers.core.host import service_running

service = 'elasticsearch'

msg_done = "Unit is ready"
msg_failure = "Loading of the dashboards and/or visualizations failed."
msg_service_not_running = "elasticsearch service is not running."

status_maintenance = 'maintenance'
status_blocked = 'blocked'
status_active = 'active'

hooks = Hooks()


@retry(stop_max_attempt_number=5, wait_fixed=12000)
def call_load_script(priv_ip, port):
    command = ["./load.sh", "-l", priv_ip + ":" + port]
    file_dir = os.path.abspath("files")
    if (call(command, cwd=file_dir) != 0):
        raise IOError("Unable to connect to elasticsearch")


def load_dashboards():
    priv_ip = unit_get('private-address')
    port = relation_get("elasticsearch_port")
    try:
        call_load_script(priv_ip, port)
        status_set(status_active, msg_done)
    except IOError:
        status_set(status_maintenance, msg_failure)


@hooks.hook('dashboard-relation-changed')
def dashboard_relation_changed():
    if service_running(service):
        load_dashboards()
    else:
        status_set(status_blocked, msg_service_not_running)


if __name__ == "__main__":
    try:
        hooks.execute(sys.argv)
    except UnregisteredHookError as e:
        juju_log('Unknown hook {} - skipping.'.format(e))
