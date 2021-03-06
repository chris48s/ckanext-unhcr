import pylons
from ckan.lib.search import rebuild
from paste.registry import Registry
from ckan.tests import helpers as core_helpers, factories as core_factories


class FunctionalTestBase(core_helpers.FunctionalTestBase):

    # Config

    @classmethod
    def setup_class(cls):
        super(FunctionalTestBase, cls).setup_class()
        core_helpers.reset_db()

        # Fix ckanext-hierarchy "c"
        c = pylons.util.AttribSafeContextObj()
        registry = Registry()
        registry.prepare()
        registry.register(pylons.c, c)

    @classmethod
    def teardown_class(cls):
        super(FunctionalTestBase, cls).teardown_class()
        core_helpers.reset_db()

    def setup(self):
        super(FunctionalTestBase, self).setup()
        core_helpers.reset_db()
        rebuild()

        # Get app
        self.app = self._get_test_app()
