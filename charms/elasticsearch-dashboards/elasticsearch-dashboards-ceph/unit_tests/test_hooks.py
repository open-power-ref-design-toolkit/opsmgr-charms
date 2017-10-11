from test_utils import CharmTestCase

from mock import call

import hooks as hooks

TO_PATCH = [
    # charmhelpers.core.hookenv
    'Hooks',
    'relation_get',
    'status_set',
    # charmhelpers.core.ansible
    'apply_playbook',
    # charmhelpers.core.python.packages
    'pip_install',
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
        self.status_set.assert_has_calls([
            call(hooks.status_maintenance, hooks.msg_install_prereqs),
            call(hooks.status_maintenance, hooks.msg_install_ansible)])

    def test_config_changed_with_relationship(self):
        self.relation_get.return_value = "9200"
        hooks.config_changed()
        self.apply_playbook.assert_called_with(hooks.playbook,
                                               tags=['config_changed'])
        self.status_set.assert_called_with(hooks.status_active,
                                           hooks.msg_service_uploaded)

    def test_config_changed_without_relationship(self):
        self.relation_get.return_value = None
        hooks.config_changed()
        self.apply_playbook.assert_not_called()
        self.status_set.assert_called_with(hooks.status_blocked,
                                           hooks.msg_missing_es_rel)
