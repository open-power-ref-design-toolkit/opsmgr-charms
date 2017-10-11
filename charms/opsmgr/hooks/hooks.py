#!/usr/bin/python

import base64
import glob
import os
import shutil
import site
import sys

from charmhelpers.core.hookenv import (
    Hooks,
    UnregisteredHookError,
    config,
    log as juju_log,
    relation_get,
    status_set,
)

from charmhelpers.contrib.openstack.utils import (
    _git_yaml_load,
    is_unit_paused_set
)

from charmhelpers.fetch import (
    apt_install,
    install_remote
)

from jinja2 import (
    Environment,
    FileSystemLoader
)

from charmhelpers.contrib.python.packages import pip_install
from charmhelpers.core.host import service_restart
from distutils.sysconfig import get_python_lib
from subprocess import call

OPSMGR_CONFIG_DIR = "/etc/opsmgr"
OPSMGR_LOG_DIR = "/var/log/opsmgr"

GIT_CLONE_PARENT_DIR = '/tmp'
SRC_ENABLED_DIR = os.path.join(GIT_CLONE_PARENT_DIR,
                               'opsmgr.git/horizon/enabled')
OS_BASE_DIR = '/usr/share/openstack-dashboard'
OPSMGR_DASHBOARD_DEST_DIR = os.path.join(OS_BASE_DIR, 'operational_mgmt')
OS_DASHBOARD_ENABLED_DIR = os.path.join(OS_BASE_DIR,
                                        'openstack_dashboard/local/enabled')
OPSMGR_UNINSTALL_DIRS = ['opsmgr', 'operational_mgmt']

required_aps = ['libffi-dev']

TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader('./files'),
    trim_blocks=True)

hooks = Hooks()


@hooks.hook('install.real')
def install():
    """ Start running the install steps """

    status_set('maintenance', 'Installing pre-req apps')
    apt_install(required_aps)

    status_set('maintenance', 'Git clone from repository')
    clone_dir = git_clone(config('openstack-origin-git'))

    status_set('maintenance', 'Running pip installs')
    do_pip_installs(config('opsmgr-plugins'), clone_dir)

    status_set('maintenance', 'Post-install')
    post_install()

    status_set('maintenance', 'Missing relationship to mysql')


def git_clone(config_yaml):
    """ Clone from git repository specified in the config.yaml.
        opsmgr is not supplied in a normal distro package the
        only install option is to specify the git url in the config.yaml.
        (No default location is specified here either in the code.)
    """
    git_repository = config('git-repository')
    git_branch = config('git-branch')
    juju_log('Git repository: {} branch: {}'.format(git_repository,
                                                    git_branch))

    depth = '1'
    parent_dir = GIT_CLONE_PARENT_DIR
    clone_dir = install_remote(git_repository, dest=parent_dir,
                               branch=git_branch, depth=depth)
    juju_log('Cloned into directory: {}'.format(clone_dir))

    return clone_dir


def do_pip_installs(plugin_yaml, clone_dir):
    """ Run pip install for the source code downloaded from the git
        clone.
    """
    for plugin in _git_yaml_load(plugin_yaml):
        plugin_dir = os.path.join(clone_dir, plugin)
        juju_log('pip install from: {}'.format(plugin_dir))
        pip_install(plugin_dir)


def post_install():
    """ Move the dashboard files into the required openstack-dashboard
        locations.
    """
    # Need to retrieve the python install dir from python
    juju_log('get_python_lib: {}'.format(get_python_lib()))
    juju_log('getsitepackages: {}'.format(site.getsitepackages()[0]))
    src_dir = site.getsitepackages()[0]

    copy_trees = {
        'opsmgrdashboard': {
            'src': os.path.join(src_dir, 'operational_mgmt'),
            'dest': os.path.join(OS_BASE_DIR, 'operational_mgmt')
        }
    }

    for name, dirs in copy_trees.iteritems():
        """ The operational_mgmt directory should not exist, but make sure
            to remove the directory if they exist before
            copying over the directory and files
        """
        if os.path.exists(dirs['dest']):
            shutil.rmtree(dirs['dest'])
        juju_log('copytree src: {} dest: {}'.format(dirs['src'], dirs['dest']))
        shutil.copytree(dirs['src'], dirs['dest'])

    """ Copy opsmgr/enabled files to openstack-dashboard
        enabled directory
    """
    copy_file_list = glob.glob(SRC_ENABLED_DIR + '/*')

    juju_log('copy_file_list: {}'.format(copy_file_list))
    for path in copy_file_list:
        shutil.copy(path, OS_DASHBOARD_ENABLED_DIR)

    """ Restart the openstack-dashboard. """
    if not is_unit_paused_set():
        service_restart('apache2')

    """ create /etc/opsmgr and /var/log/opsmgr """
    if not os.path.exists(OPSMGR_CONFIG_DIR):
        os.mkdir(OPSMGR_CONFIG_DIR)
        os.chmod(OPSMGR_CONFIG_DIR, 0755)
    if not os.path.exists(OPSMGR_LOG_DIR):
        os.mkdir(OPSMGR_LOG_DIR)
        os.chmod(OPSMGR_LOG_DIR, 0777)
        # create empty files with permissions so everyone can write
        open(os.path.join(OPSMGR_LOG_DIR, 'opsmgr.log'), 'a').close()
        open(os.path.join(OPSMGR_LOG_DIR, 'opsmgr_error.log'), 'a').close()
        os.chmod(os.path.join(OPSMGR_LOG_DIR, 'opsmgr.log'), 0666)
        os.chmod(os.path.join(OPSMGR_LOG_DIR, 'opsmgr_error.log'), 0666)

    """ copy logging.yaml to /etc/opsmgr """
    shutil.copyfile('files/logging.yaml',
                    os.path.join(OPSMGR_CONFIG_DIR, 'logging.yaml'))


def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


def get_random_passphrase():
    """
    Generate a random passphrase to encyipt passwords in the database.
    The password needs to be preserved so if config-changed is run
    again the same passpphrase is used to decrypt the system passwords.
    """

    passphrase_file = os.path.join(OPSMGR_CONFIG_DIR, '.passphrase')
    if os.path.exists(passphrase_file):
        with open(passphrase_file, 'r') as input:
            passphrase = input.readline().strip()
    else:
        passphrase = str(base64.b64encode(os.urandom(32)))
        with open(passphrase_file, 'w') as output:
            output.write(passphrase)
    return passphrase


@hooks.hook('mysql-relation-changed')
def mysql_relation_changed():

    status_set('maintenance', 'Configuring db')

    """ passphrase to encrypt passwords in the db """
    passphrase = get_random_passphrase()

    """ get the db connection info to use """
    db_name = relation_get('database')
    db_user = relation_get('user')
    db_pass = relation_get('password')
    db_host = relation_get('host')

    """ Create the opsmg.conf file based on the template """
    context = {
        'db_name': db_name,
        'db_user': db_user,
        'db_password': db_pass,
        'db_host': db_host,
        'random_passphrase': passphrase
    }
    opsmgr_config_file = os.path.join(OPSMGR_CONFIG_DIR, 'opsmgr.conf')
    with open(opsmgr_config_file, 'w') as f:
        render_text = render_template('opsmgr.conf.j2', context)
        f.write(render_text)

    """ Create database tables """
    call(["opsmgr-admin", "db_sync"])

    """ add default rack """
    call(["opsmgr", "add_rack", "-l", "default"])

    status_set('active', 'Unit is ready')


@hooks.hook('stop')
def trove_dashboard_uninstall(relation_id=None):
    """ Start running the uninstall steps """
    status_set('maintenance', 'Remove dashboard files')
    remove_dashboard_files()

    status_set('maintenance', 'Remove source files')
    remove_source_files()

    """ Restart the openstack-dashboard. """
    if not is_unit_paused_set():
        service_restart('apache2')

    status_set('active', 'opsmgr uninstalled')


def remove_dashboard_files():
    """ Remove the directories and files from the openstack-dashboard
        locations.
    """
    if os.path.exists(OPSMGR_DASHBOARD_DEST_DIR):
        shutil.rmtree(OPSMGR_DASHBOARD_DEST_DIR)

    delete_files = {
        '_4000_': os.path.join(OS_DASHBOARD_ENABLED_DIR, '_4000_operational_mgmt.py'),  # noqa: E501
        '_4000_pyc': os.path.join(OS_DASHBOARD_ENABLED_DIR, '_4000_operational_mgmt.py'),  # noqa: E501
        '_4050_': os.path.join(OS_DASHBOARD_ENABLED_DIR, '_4050_operational_mgmt_inventory_panel.py'),  # noqa: E501
        '_4050_pyc': os.path.join(OS_DASHBOARD_ENABLED_DIR, '_4050_operational_mgmt_inventory_panel.pyc'),  # noqa: E501
    }

    for name, files in delete_files.iteritems():
        if os.path.exists(files):
            os.remove(files)


def remove_source_files():
    """ Remove the directories and files from the dist-packages python
        install location.  Since the trove dashboard was installed from
        source, pip uninstall will not uninstall the trove dashboard
        since there was no package for the install.
    """
    juju_log('getsitepackages: {}'.format(site.getsitepackages()[0]))
    py_install_dir = site.getsitepackages()[0]

    for directory in OPSMGR_UNINSTALL_DIRS:
        uninstall_dir = os.path.join(py_install_dir, directory)

        if os.path.exists(uninstall_dir):
            shutil.rmtree(uninstall_dir)

        # Make sure to remove egg directories and pth files
        uninstall_dir = os.path.join(py_install_dir, directory + '*')
        uninstall_dir_list = glob.glob(uninstall_dir)
        juju_log('uninstall_dir_list: {}'.format(uninstall_dir_list))
        for path in uninstall_dir_list:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

    # Remove the opsmgr bin file
    if os.path.exists('/usr/local/bin/opsmgr'):
        os.remove('/usr/local/bin/opsmgr')
    if os.path.exists('/user/local/bin/opsmgr-admin'):
        os.remove('/user/local/bin/opsmgr-admin')


def main():
    try:
        hooks.execute(sys.argv)
    except UnregisteredHookError as e:
        juju_log('Unknown hook {} - skipping.'.format(e))


if __name__ == '__main__':
    main()
