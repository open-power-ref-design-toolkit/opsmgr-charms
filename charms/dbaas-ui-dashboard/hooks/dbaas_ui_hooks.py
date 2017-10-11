#!/usr/bin/python

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
    status_set,
    relation_get,
)

from charmhelpers.contrib.openstack.utils import (
    _git_yaml_load,
    error_out,
    is_unit_paused_set,
    get_os_codename_package,
)

from charmhelpers.fetch import (
    install_remote,
)

from charmhelpers.contrib.python.packages import (
    pip_install,
)

from charmhelpers.core.host import (
    service_restart,
)

from distutils.sysconfig import get_python_lib

DBAAS_UI_DASHBOARD = 'dbaas-ui-dashboard'
GIT_CLONE_PARENT_DIR = '/tmp'
DBAAS_UI_SRC_PATH = 'osa/dbaas_ui'
DBAAS_UI_CLONE_DIR = '/tmp/dbaas'
NEWTON_OPENSTACK_DASHBOARD_IMG_DIR = \
    '/usr/share/openstack-dashboard/openstack_dashboard/static/dashboard/img'
OCATA_OPENSTACK_DASHBOARD_IMG_DIR = \
    '/var/lib/openstack-dashboard/static/dashboard/img'
OPENSTACK_DASHBOARD_ENABLED_DIR = \
    '/usr/share/openstack-dashboard/openstack_dashboard/local/enabled'
DBAAS_UI_DEST_DIR = '/usr/share/openstack-dashboard/dbaas_ui'
DBAAS_UI_DASHBOARD_UNINSTALL_DIR = 'dbaas_ui'
DASHBOARD_PACKAGE = 'openstack-dashboard'

hooks = Hooks()


@hooks.hook('install.real')
def dbaas_ui_dashboard_install(relation_id=None):
    """ Start running the install steps """
    if relation_get('trove_plugin') is None:
        status_set('blocked', 'Missing trove-dashboard relationship')
        return

    dbaas_ui_dashboard_run_install()


def dbaas_ui_dashboard_run_install():
    """ Run the install steps """

    """ If someone removes and adds back the trove-dashboard relation,
        no need to try to re-install here
    """
    install_dir_file = os.path.join(OPENSTACK_DASHBOARD_ENABLED_DIR,
                                    '_4114_database_ui_dashboard.py')
    if os.path.exists(install_dir_file):
        juju_log('dbaas_ui_installed: {}'.format(install_dir_file))
        status_set('active', 'Unit is ready')
        return

    status_set('maintenance', 'Git clone from repository')
    clone_dir = dbaas_ui_dashboard_git_clone(config('openstack-origin-git'))

    status_set('maintenance', 'Running pip install')
    dbaas_ui_dashboard_pip_install(config('openstack-origin-git'), clone_dir)

    status_set('maintenance', 'Post-install')
    dbaas_ui_dashboard_git_post_install(clone_dir)

    status_set('active', 'Unit is ready')


def dbaas_ui_dashboard_git_clone(config_yaml):
    """ Clone from git repository specified in the config.yaml.
        Assuming here the dbaas_ui dashboard is not supplied in a
        normal distro package, meaning the only install option is
        to specify the git url in the config.yaml.  (No default
        location is specified here either in the code.)
    """
    config = _git_yaml_load(config_yaml)

    git_repository = None
    for c in config['repositories']:
        if c['name'] == DBAAS_UI_DASHBOARD:
            git_repository = c['repository']
            git_branch = c['branch']

    if git_repository is None:
        error_out('Missing repository in config.yaml')

    juju_log('Git repository: {} branch: {}'.format(git_repository,
                                                    git_branch))

    depth = '1'
    parent_dir = GIT_CLONE_PARENT_DIR
    clone_dir = install_remote(git_repository, dest=parent_dir,
                               branch=git_branch, depth=depth)
    juju_log('Cloned into directory: {}'.format(clone_dir))

    return clone_dir


def dbaas_ui_dashboard_pip_install(config_yaml, clone_dir):
    """ Run pip install for the source code downloaded from the git
        clone.
    """
    src_dir = os.path.join(clone_dir, DBAAS_UI_SRC_PATH)
    if os.path.exists(DBAAS_UI_CLONE_DIR):
        shutil.rmtree(DBAAS_UI_CLONE_DIR)
    shutil.copytree(src_dir, DBAAS_UI_CLONE_DIR)
    juju_log('pip install from: {}'.format(DBAAS_UI_CLONE_DIR))
    pip_install(DBAAS_UI_CLONE_DIR)


def dbaas_ui_dashboard_git_post_install(clone_dir):
    """ Move the dbaas_ui-dashboard files into the required openstack-dashboard
        locations.
    """
    src_dir = os.path.join(clone_dir, DBAAS_UI_SRC_PATH)
    img_src_dir = os.path.join(src_dir, 'IDL-Images')
    src_files = os.listdir(img_src_dir)

    openstack_codename = get_os_codename_package(DASHBOARD_PACKAGE)
    juju_log('openstack codename: {}'.format(openstack_codename))

    """ Should really get the static directory location from the
        openstack-dashboard, but there is no interface defined
        for that function, and also there is no charm helper
        defined either to retrieve the directory
    """
    if openstack_codename == 'newton':
        img_dest_dir = NEWTON_OPENSTACK_DASHBOARD_IMG_DIR
    else:
        img_dest_dir = OCATA_OPENSTACK_DASHBOARD_IMG_DIR

    juju_log('copy files src: {} dest: {}'.format(img_src_dir, img_dest_dir))
    for file_name in src_files:
        path_and_file_name = os.path.join(img_src_dir, file_name)
        if os.path.isfile(path_and_file_name):
            shutil.copy(path_and_file_name, img_dest_dir)

    enabled_src_dir = os.path.join(src_dir, 'enabled_ui')
    src_files = os.listdir(enabled_src_dir)

    juju_log('copy files src: {} dest: '
             '{}'.format(enabled_src_dir, OPENSTACK_DASHBOARD_ENABLED_DIR))
    for file_name in src_files:
        path_and_file_name = os.path.join(enabled_src_dir, file_name)
        if os.path.isfile(path_and_file_name):
            shutil.copy(path_and_file_name, OPENSTACK_DASHBOARD_ENABLED_DIR)

    # Need to retrieve the python install dir from python
    juju_log('get_python_lib: {}'.format(get_python_lib()))
    juju_log('getsitepackages: {}'.format(site.getsitepackages()[0]))
    src_dir = site.getsitepackages()[0]

    installed_src_dir = os.path.join(src_dir, 'dbaas_ui')
    """ The dbaas-ui-dashboard openstack-dashboard directory should not exist,
        but make sure to remove the directory if it exists before
        copying over the directory, sub-directories, and files
    """
    if os.path.exists(DBAAS_UI_DEST_DIR):
        shutil.rmtree(DBAAS_UI_DEST_DIR)
    juju_log('copytree src: {} dest: {}'.format(installed_src_dir,
                                                DBAAS_UI_DEST_DIR))
    shutil.copytree(installed_src_dir, DBAAS_UI_DEST_DIR)

    """ Restart the openstack-dashboard. """
    if not is_unit_paused_set():
        service_restart('apache2')


@hooks.hook('trove-plugin-relation-joined')
def dbaas_ui_dashboard_relation_joined():
    """ add-relation has been run """
    juju_log('trove-plugin-relation-joined hook run')


@hooks.hook('trove-plugin-relation-changed')
def dbaas_ui_dashboard_relation_changed():
    """ add-relation has been run """
    _hook = 'trove-plugin-relation-changed'
    juju_log('{} hook run'.format(_hook))
    trove_plugin_relation = relation_get('trove_plugin')
    juju_log('{} relation: {}'.format(_hook, trove_plugin_relation))

    if trove_plugin_relation is None:
        return

    dbaas_ui_dashboard_run_install()


@hooks.hook('trove-plugin-relation-departed')
def dbaas_ui_dashboard_relation_departed():
    """ remove-relation has been run """
    juju_log('trove-plugin-relation-departed hook run')


@hooks.hook('trove-plugin-relation-broken')
def dbaas_ui_dashboard_relation_broken():
    """ remove-relation has been run """
    juju_log('trove-plugin-relation-broken hook run')

    if relation_get('trove_plugin') is None:
        status_set('blocked', 'Missing trove-dashboard relationship')


@hooks.hook('stop')
def dbaas_ui_dashboard_uninstall(relation_id=None):
    """ Start running the uninstall steps """
    status_set('maintenance', 'Remove dashboard files')
    dbaas_ui_dashboard_remove_dashboard_files()

    status_set('maintenance', 'Remove source files')
    dbaas_ui_dashboard_remove_source_files()

    """ Restart the openstack-dashboard. """
    if not is_unit_paused_set():
        service_restart('apache2')

    status_set('active', 'dbaas-ui-dashboard stopped')


def dbaas_ui_dashboard_remove_dashboard_files():
    """ Remove the directories and files from the openstack-dashboard
        locations.
    """
    if os.path.exists(DBAAS_UI_DEST_DIR):
        shutil.rmtree(DBAAS_UI_DEST_DIR)

    delete_enabled_files = {
        '_4114_': os.path.join(OPENSTACK_DASHBOARD_ENABLED_DIR, '_4114_database_ui_dashboard.py'),  # noqa: E501
        '_4114_pyc': os.path.join(OPENSTACK_DASHBOARD_ENABLED_DIR, '_4114_database_ui_dashboard.pyc'),  # noqa: E501
        '_4115_': os.path.join(OPENSTACK_DASHBOARD_ENABLED_DIR, '_4115_database_ui_shortcuts.py'),  # noqa: E501
        '_4115_pyc': os.path.join(OPENSTACK_DASHBOARD_ENABLED_DIR, '_4115_database_ui_shortcuts.pyc'),  # noqa: E501
        '_4116_': os.path.join(OPENSTACK_DASHBOARD_ENABLED_DIR, '_4116_database_ui_instances.py'),  # noqa: E501
        '_4116_pyc': os.path.join(OPENSTACK_DASHBOARD_ENABLED_DIR, '_4116_database_ui_instances.pyc'),  # noqa: E501
        '_4117_': os.path.join(OPENSTACK_DASHBOARD_ENABLED_DIR, '_4117_database_ui_backups.py'),  # noqa: E501
        '_4117_pyc': os.path.join(OPENSTACK_DASHBOARD_ENABLED_DIR, '_4117_database_ui_backups.pyc'),  # noqa: E501
    }

    for name, files in delete_enabled_files.iteritems():
        if os.path.exists(files):
            os.remove(files)

    openstack_codename = get_os_codename_package(DASHBOARD_PACKAGE)
    juju_log('openstack codename: {}'.format(openstack_codename))

    if openstack_codename == 'newton':
        img_dir = NEWTON_OPENSTACK_DASHBOARD_IMG_DIR
    else:
        img_dir = OCATA_OPENSTACK_DASHBOARD_IMG_DIR

    delete_img_files = {
        'AddDatabase': os.path.join(img_dir, 'AddDatabase.svg'),
        'CreateBackup': os.path.join(img_dir, 'CreateBackup.svg'),
        'CreateDatabase': os.path.join(img_dir, 'CreateDatabase.svg'),
        'CreateUser': os.path.join(img_dir, 'CreateUser.svg'),
        'DeleteBackup': os.path.join(img_dir, 'DeleteBackup.svg'),
        'DeleteDatabase': os.path.join(img_dir, 'DeleteDatabase.svg'),
        'DeleteInstance': os.path.join(img_dir, 'DeleteInstance.svg'),
        'DeleteUser': os.path.join(img_dir, 'DeleteUser.svg'),
        'EditInstance': os.path.join(img_dir, 'EditInstance.svg'),
        'EnabledRoot': os.path.join(img_dir, 'EnableRoot.svg'),
        'GrantAccess': os.path.join(img_dir, 'GrantAccess.svg'),
        'LaunchBackup': os.path.join(img_dir, 'LaunchBackup.svg'),
        'LaunchInstance': os.path.join(img_dir, 'LaunchInstance.svg'),
        'manage_24': os.path.join(img_dir, 'manage_24.svg'),
        'ManageRoot14': os.path.join(img_dir, 'ManageRoot-14.svg'),
        'ManageUser': os.path.join(img_dir, 'ManageUser.svg'),
        'ResizeInstance': os.path.join(img_dir, 'ResizeInstance.svg'),
        'RestartInstance17': os.path.join(img_dir, 'RestartInstance-17.svg'),
        'RevokeAccess': os.path.join(img_dir, 'RevokeAccess.svg'),
        'RevoteAccess': os.path.join(img_dir, 'RevoteAccess.svg'),
        'RootDisable': os.path.join(img_dir, 'RootDisable.svg'),
        'secure_24': os.path.join(img_dir, 'secure_24.png'),
        'UpgradeInstance': os.path.join(img_dir, 'UpgradeInstance.svg'),
        'view_24': os.path.join(img_dir, 'view_24.svg'),
    }

    for name, files in delete_img_files.iteritems():
        if os.path.exists(files):
            os.remove(files)


def dbaas_ui_dashboard_remove_source_files():
    """ Remove the directories and files from the dist-packages python
        install location.  Since the dbaas_ui dashboard was installed from
        source, pip uninstall will not uninstall the dbaas_ui dashboard
        since there was no package for the install.
    """
    juju_log('getsitepackages: {}'.format(site.getsitepackages()[0]))
    py_install_dir = site.getsitepackages()[0]
    uninstall_dir = os.path.join(py_install_dir,
                                 DBAAS_UI_DASHBOARD_UNINSTALL_DIR)

    if os.path.exists(uninstall_dir):
        shutil.rmtree(uninstall_dir)

    # Make sure to remove all dbaas_ui_dashboard directories
    uninstall_dir = os.path.join(py_install_dir,
                                 DBAAS_UI_DASHBOARD_UNINSTALL_DIR + '*')
    uninstall_dir_list = glob.glob(uninstall_dir)
    juju_log('uninstall_dir_list: {}'.format(uninstall_dir_list))
    for path in uninstall_dir_list:
        if os.path.isdir(path):
            shutil.rmtree(path)


def main():
    try:
        hooks.execute(sys.argv)
    except UnregisteredHookError as e:
        juju_log('Unknown hook {} - skipping.'.format(e))


if __name__ == '__main__':
    main()
