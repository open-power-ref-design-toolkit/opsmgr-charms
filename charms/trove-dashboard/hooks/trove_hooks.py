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
    relation_set,
    relation_ids,
    relation_clear,
)

from charmhelpers.contrib.openstack.utils import (
    _git_yaml_load,
    error_out,
    is_unit_paused_set
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

TROVE_DASHBOARD = 'trove-dashboard'
GIT_CLONE_PARENT_DIR = '/tmp'
PYTHON_INSTALL_DIR = '/usr/local/lib/python2.7/dist-packages'
TROVE_DASHBOARD_DEST_DIR = '/usr/share/openstack-dashboard/trove_dashboard'
TROVECLIENT_DEST_DIR = '/usr/share/openstack-dashboard/troveclient'
TROVE_DASHBOARD_ENABLED_DIR = \
    '/usr/share/openstack-dashboard/trove_dashboard/enabled'
OPENSTACK_DASHBOARD_ENABLED_DIR = \
     '/usr/share/openstack-dashboard/openstack_dashboard/local/enabled'
TROVE_DASHBOARD_UNINSTALL_DIR = 'trove_dashboard'
TROVECLIENT_UNINSTALL_DIR = 'troveclient'
PYTHON_TROVECLIENT_UNINSTALL_DIR = 'python_troveclient'

hooks = Hooks()


@hooks.hook('install.real')
def trove_dashboard_install(relation_id=None):
    """ Start running the install steps """
    status_set('maintenance', 'Git clone from repository')
    clone_dir = trove_dashboard_git_clone(config('openstack-origin-git'))

    status_set('maintenance', 'Running pip install')
    trove_dashboard_pip_install(config('openstack-origin-git'), clone_dir)

    status_set('maintenance', 'Post-install')
    trove_dashboard_git_post_install()

    status_set('active', 'Unit is ready')


def trove_dashboard_git_clone(config_yaml):
    """ Clone from git repository specified in the config.yaml.
        Assuming here the trove dashboard is not supplied in a
        normal distro package, meaning the only install option is
        to specify the git url in the config.yaml.  (No default
        location is specified here either in the code.)
    """
    config = _git_yaml_load(config_yaml)

    git_repository = None
    for c in config['repositories']:
        if c['name'] == TROVE_DASHBOARD:
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


def trove_dashboard_pip_install(config_yaml, clone_dir):
    """ Run pip install for the source code downloaded from the git
        clone.
    """
    juju_log('pip install from: {}'.format(clone_dir))
    pip_install(clone_dir)


def trove_dashboard_git_post_install():
    """ Move the trove-dashboard files into the required openstack-dashboard
        locations.
    """
    # Need to retrieve the python install dir from python
    juju_log('get_python_lib: {}'.format(get_python_lib()))
    juju_log('getsitepackages: {}'.format(site.getsitepackages()[0]))
    src_dir = site.getsitepackages()[0]

    copy_trees = {
        'trovedashboard': {
            'src': os.path.join(src_dir, 'trove_dashboard'),
            'dest': TROVE_DASHBOARD_DEST_DIR,
        },
        'troveclient': {
            'src': os.path.join(src_dir, 'troveclient'),
            'dest': TROVECLIENT_DEST_DIR,
        },
    }

    for name, dirs in copy_trees.iteritems():
        """ The trove_dashboard and troveclient directories should not exist,
             but make sure to remove the directories if they exist before
            copying over the directories and files
        """
        if os.path.exists(dirs['dest']):
            shutil.rmtree(dirs['dest'])
        juju_log('copytree src: {} dest: {}'.format(dirs['src'], dirs['dest']))
        shutil.copytree(dirs['src'], dirs['dest'])

    """ Copy trove_dashboard/enabled files to openstack-dashboard
        enabled directory
    """
    copy_file_list = glob.glob(TROVE_DASHBOARD_ENABLED_DIR + '/*')

    juju_log('copy_file_list: {}'.format(copy_file_list))
    for path in copy_file_list:
        shutil.copy(path, OPENSTACK_DASHBOARD_ENABLED_DIR)

    """ Restart the openstack-dashboard. """
    if not is_unit_paused_set():
        service_restart('apache2')


@hooks.hook('trove-plugin-relation-joined')
def trove_dashboard_relation_joined():
    """ add-relation has been run """
    juju_log('trove-plugin-relation-joined hook run')
    # The trove-dashboard plug-in is running
    relation_set(trove_plugin=True)


@hooks.hook('trove-plugin-relation-changed')
def trove_dashboard_relation_changed():
    """ add-relation has been run """
    juju_log('trove-plugin-relation-changed hook run')


@hooks.hook('trove-plugin-relation-departed')
def trove_dashboard_relation_departed():
    """ remove-relation has been run """
    juju_log('trove-plugin-relation-departed hook run')

    juju_log('relation_ids: {}'.format(relation_ids('trove-plugin')))
    for rel_id in relation_ids('trove-plugin'):
        relation_clear(rel_id)


@hooks.hook('trove-plugin-relation-broken')
def trove_dashboard_relation_broken():
    """ remove-relation has been run """
    juju_log('trove-plugin-relation-broken hook run')


@hooks.hook('stop')
def trove_dashboard_uninstall(relation_id=None):
    """ Start running the uninstall steps """
    status_set('maintenance', 'Remove dashboard files')
    trove_dashboard_remove_dashboard_files()

    status_set('maintenance', 'Remove source files')
    trove_dashboard_remove_source_files()

    """ Restart the openstack-dashboard. """
    if not is_unit_paused_set():
        service_restart('apache2')

    status_set('active', 'trove-dashboard stopped')


def trove_dashboard_remove_dashboard_files():
    """ Remove the directories and files from the openstack-dashboard
        locations.
    """
    if os.path.exists(TROVE_DASHBOARD_DEST_DIR):
        shutil.rmtree(TROVE_DASHBOARD_DEST_DIR)

    if os.path.exists(TROVECLIENT_DEST_DIR):
        shutil.rmtree(TROVECLIENT_DEST_DIR)

    delete_files = {
        '_1710_': os.path.join(OPENSTACK_DASHBOARD_ENABLED_DIR, '_1710_database_panel_group.py'),  # noqa: E501
        '_1710_pyc': os.path.join(OPENSTACK_DASHBOARD_ENABLED_DIR, '_1710_database_panel_group.pyc'),  # noqa: E501
        '_1720_': os.path.join(OPENSTACK_DASHBOARD_ENABLED_DIR, '_1720_project_databases_panel.py'),  # noqa: E501
        '_1720_pyc': os.path.join(OPENSTACK_DASHBOARD_ENABLED_DIR, '_1720_project_databases_panel.pyc'),  # noqa: E501
        '_1730_': os.path.join(OPENSTACK_DASHBOARD_ENABLED_DIR, '_1730_project_database_backups_panel.py'),  # noqa: E501
        '_1730_pyc': os.path.join(OPENSTACK_DASHBOARD_ENABLED_DIR, '_1730_project_database_backups_panel.pyc'),  # noqa: E501
        '_1731_': os.path.join(OPENSTACK_DASHBOARD_ENABLED_DIR, '_1731_project_database_backups_panel.py'),  # noqa: E501
        '_1731_pyc': os.path.join(OPENSTACK_DASHBOARD_ENABLED_DIR, '_1731_project_database_backups_panel.pyc'),  # noqa: E501
        '_1740_': os.path.join(OPENSTACK_DASHBOARD_ENABLED_DIR, '_1740_project_database_clusters_panel.py'),  # noqa: E501
        '_1740_pyc': os.path.join(OPENSTACK_DASHBOARD_ENABLED_DIR, '_1740_project_database_clusters_panel.pyc'),  # noqa: E501
        '_1760_': os.path.join(OPENSTACK_DASHBOARD_ENABLED_DIR, '_1760_project_database_configurations_panel.py'),  # noqa: E501
        '_1760_pyc': os.path.join(OPENSTACK_DASHBOARD_ENABLED_DIR, '_1760_project_database_configurations_panel.pyc'),  # noqa: E501
    }

    for name, files in delete_files.iteritems():
        if os.path.exists(files):
            os.remove(files)


def trove_dashboard_remove_source_files():
    """ Remove the directories and files from the dist-packages python
        install location.  Since the trove dashboard was installed from
        source, pip uninstall will not uninstall the trove dashboard
        since there was no package for the install.
    """
    juju_log('getsitepackages: {}'.format(site.getsitepackages()[0]))
    py_install_dir = site.getsitepackages()[0]
    uninstall_dir = os.path.join(py_install_dir, TROVE_DASHBOARD_UNINSTALL_DIR)

    if os.path.exists(uninstall_dir):
        shutil.rmtree(uninstall_dir)

    # Make sure to remove all trove_dashboard directories
    uninstall_dir = os.path.join(py_install_dir,
                                 TROVE_DASHBOARD_UNINSTALL_DIR + '*')
    uninstall_dir_list = glob.glob(uninstall_dir)
    juju_log('uninstall_dir_list: {}'.format(uninstall_dir_list))
    for path in uninstall_dir_list:
        if os.path.isdir(path):
            shutil.rmtree(path)

    uninstall_dir = os.path.join(py_install_dir, TROVECLIENT_UNINSTALL_DIR)

    if os.path.exists(uninstall_dir):
        shutil.rmtree(uninstall_dir)

    # Make sure to remove all python_troveclient directories
    uninstall_dir = os.path.join(py_install_dir,
                                 PYTHON_TROVECLIENT_UNINSTALL_DIR + '*')
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
