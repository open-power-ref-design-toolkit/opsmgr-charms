from test_utils import CharmTestCase

from mock import call

import hooks as hooks

TO_PATCH = [
    # charmhelpers.core.hookenv
    'Hooks',
    'status_set',
    # charmhelpers.core.ansible
    'apply_playbook',
    # charmhelpers.core.python.packages
    'pip_install',
    # charmhelpers.core.host
    'service_running',
    # charmhelpers.fetch
    'apt_install'
]


class HookTests(CharmTestCase):

    def setUp(self):
        super(HookTests, self).setUp(hooks, TO_PATCH)

    def test_install_hook(self):
        hooks.install2()
        self.apt_install.assert_called_with(hooks.required_aps)
        self.pip_install.assert_called_with(hooks.required_pip_packages,
                                            fatal=True)
        self.apply_playbook.assert_called_with(hooks.playbook,
                                               tags=['install'])
        self.status_set.assert_has_calls([
            call(hooks.status_maintenance, hooks.msg_install_prereqs),
            call(hooks.status_maintenance, hooks.msg_install_ansible),
            call(hooks.status_maintenance, hooks.msg_install_service)])

    def test_config_changed(self):
        hooks.config_changed()
        self.apply_playbook.assert_called_with(hooks.playbook,
                                               tags=['config_changed'])
        self.status_set.assert_called_with(hooks.status_maintenance,
                                           hooks.msg_config_changed)

    def test_start(self):
        self.service_running.return_value = False
        hooks.start()
        self.apply_playbook.assert_called_with(hooks.playbook, tags=['start'])
        self.status_set.assert_called_with(hooks.status_maintenance,
                                           hooks.msg_service_failed_to_start)

    def test_stop(self):
        hooks.stop()
        self.apply_playbook.assert_called_with(hooks.playbook, tags=['stop'])

    def test_update_status(self):
        self.service_running.return_value = True
        hooks.update_status()
        self.status_set.assert_called_with(hooks.status_active,
                                           hooks.msg_service_running)

        self.service_running.return_value = False
        hooks.update_status()
        self.status_set.assert_called_with(hooks.status_maintenance,
                                           hooks.msg_service_stopped)
