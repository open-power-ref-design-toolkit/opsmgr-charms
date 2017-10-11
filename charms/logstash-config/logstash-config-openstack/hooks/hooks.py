#!/usr/bin/env python

import os
import shutil
import sys

from charmhelpers.core.hookenv import (
    Hooks,
    log as juju_log,
    status_set,
    UnregisteredHookError
)

from charmhelpers.core.host import (
    service_restart
)

LOGSTASH_CONFIG_DIR = '/etc/logstash/conf.d'
LOGSTASH_PATTERNS_DIR = '/etc/logstash/patterns'

msg_config_dir_missing = "Logstash configuration directory is missing."
msg_done = "Unit is ready"

status_blocked = 'blocked'
status_active = 'active'

hooks = Hooks()


def copy_config_files():
    """ copy all logstash filters in the 'files' directory
        to /etc/logstash/conf.d
    """
    src_files = os.listdir("./files")
    for file_name in src_files:
        full_file_name = os.path.join("./files", file_name)
        shutil.copy(full_file_name, LOGSTASH_CONFIG_DIR)


def copy_patterns():
    """ Copy any patterns in the optional 'patterns' charm directory
        to /etc/logstash/patterns
    """
    if os.path.isdir("./patterns"):
        if not os.path.exists(LOGSTASH_PATTERNS_DIR):
            os.mkdir(LOGSTASH_PATTERNS_DIR)
        src_files = os.listdir("./patterns")
        for file_name in src_files:
            full_file_name = os.path.join("./patterns", file_name)
            shutil.copy(full_file_name, LOGSTASH_PATTERNS_DIR)


def create_config_file():
    copy_config_files()
    copy_patterns()
    status_set(status_active, msg_done)
    service_restart('logstash')


@hooks.hook('config-changed')
def config_changed():
    if os.path.isdir(LOGSTASH_CONFIG_DIR):
        create_config_file()
    else:
        status_set(status_blocked, msg_config_dir_missing)


if __name__ == "__main__":
    try:
        hooks.execute(sys.argv)
    except UnregisteredHookError as e:
        juju_log('Unknown hook {} - skipping.'.format(e))
