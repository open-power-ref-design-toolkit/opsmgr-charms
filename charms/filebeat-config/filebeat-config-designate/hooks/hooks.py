#!/usr/bin/env python

import os
import sys
from charmhelpers.core.hookenv import (
    Hooks,
    config,
    log as juju_log,
    UnregisteredHookError,
    status_get,
    status_set
)

from charmhelpers.core.host import (
    service_restart
)

from jinja2 import (
    Environment,
    FileSystemLoader
)

TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader('./templates'),
    trim_blocks=True)

TEMPLATE_FILENAME = 'filebeat_conf.yml.j2'

FILEBEAT_CONFIG_DIR = '/etc/filebeat/conf'

msg_config_dir_missing = \
    "Filebeat configuration directory is missing. Is Filebeat installed?"
msg_generate_config = "Generating config file"
msg_done = "Unit is ready"

status_maintenance = 'maintenance'
status_blocked = 'blocked'
status_active = 'active'

hooks = Hooks()


def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


def get_context():
    paths = config('paths')
    tags = config('tags')
    multiline_pattern = config('multiline_pattern')
    multiline_negate = config('multiline_negate')
    multiline_match = config('multiline_match')
    multiline_max_lines = config('multiline_max_lines')
    multiline_timeout = config('multiline_timeout')
    encoding = config('encoding')
    exclude_lines = config('exclude_lines')
    include_lines = config('include_lines')
    exclude_files = config('exclude_files')
    context = {
        'paths': paths,
        'tags': tags,
        'multiline_pattern': multiline_pattern,
        'multiline_negate': multiline_negate,
        'multiline_match': multiline_match,
        'multiline_max_lines': multiline_max_lines,
        'multiline_timeout': multiline_timeout,
        'encoding': encoding,
        'exclude_lines': exclude_lines,
        'include_lines': include_lines,
        'exclude_files': exclude_files
    }
    return context


def create_config_file():

    status_set(status_maintenance, msg_generate_config)
    fname = os.path.join(FILEBEAT_CONFIG_DIR, config('filename'))
    context = get_context()

    with open(fname, 'w') as f:
        render_txt = render_template(TEMPLATE_FILENAME, context)
        f.write(render_txt)
    status_set(status_active, msg_done)
    service_restart('filebeat')


@hooks.hook('config-changed')
def config_changed():
    if os.path.isdir(FILEBEAT_CONFIG_DIR):
        create_config_file()
    else:
        status_set(status_blocked, msg_config_dir_missing)


@hooks.hook('update-status')
def update_status():
    (status, message) = status_get()
    # if status is blocked rerun config changed to see
    # if we are now unblocked
    if status == status_blocked:
        config_changed()


if __name__ == "__main__":
    try:
        hooks.execute(sys.argv)
    except UnregisteredHookError as e:
        juju_log('Unknown hook {} - skipping.'.format(e))
