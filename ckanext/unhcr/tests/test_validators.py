import os
import pylons
from ckan import model
from ckan.plugins import toolkit
from paste.registry import Registry
from nose.plugins.attrib import attr
import ckan.lib.navl.dictization_functions as df
from ckan.tests import factories as core_factories
from nose.tools import assert_raises, assert_equals
from ckan.tests.helpers import call_action, FunctionalTestBase
from ckanext.unhcr.tests import factories
from ckanext.unhcr import validators


class TestValidators(FunctionalTestBase):

    # Config

    @classmethod
    def setup_class(cls):

        # Hack because the hierarchy extension uses c in some methods
        # that are called outside the context of a web request
        c = pylons.util.AttribSafeContextObj()
        registry = Registry()
        registry.prepare()
        registry.register(pylons.c, c)

        super(TestValidators, cls).setup_class()

    def setup(self):
        super(TestValidators, self).setup()
        self.normal_user = core_factories.User()
        self.sysadmin = core_factories.Sysadmin()

    # Deposited Datasets

    def test_deposited_dataset_owner_org(self):
        deposit = factories.DataContainer(id='data-deposit')
        target = factories.DataContainer(id='data-target')
        result = validators.deposited_dataset_owner_org('data-deposit', {})
        assert_equals(result, 'data-deposit')

    def test_deposited_dataset_owner_org_invalid(self):
        deposit = factories.DataContainer(id='data-deposit')
        target = factories.DataContainer(id='data-target')
        assert_raises(toolkit.Invalid,
            validators.deposited_dataset_owner_org, 'data-target', {})

    def test_deposited_dataset_owner_org_dest(self):
        deposit = factories.DataContainer(id='data-deposit')
        target = factories.DataContainer(id='data-target')
        result = validators.deposited_dataset_owner_org_dest('data-target', {})
        assert_equals(result, 'data-target')

    def test_deposited_dataset_owner_org_dest_invalid_data_deposit(self):
        deposit = factories.DataContainer(id='data-deposit')
        target = factories.DataContainer(id='data-target')
        assert_raises(toolkit.Invalid,
            validators.deposited_dataset_owner_org_dest, 'data-deposit', {})

    def test_deposited_dataset_owner_org_dest_invalid_not_existent(self):
        deposit = factories.DataContainer(id='data-deposit')
        target = factories.DataContainer(id='data-target')
        assert_raises(toolkit.Invalid,
            validators.deposited_dataset_owner_org_dest, 'not-existent', {})

    def test_deposited_dataset_curation_state(self):
        assert_equals(validators.deposited_dataset_curation_state('draft', {}), 'draft')
        assert_equals(validators.deposited_dataset_curation_state('submitted', {}), 'submitted')
        assert_equals(validators.deposited_dataset_curation_state('review', {}), 'review')

    def test_deposited_dataset_curation_state_invalid(self):
        assert_raises(toolkit.Invalid,
            validators.deposited_dataset_curation_state, 'invalid', {})

    def test_deposited_dataset_curation_id_invalid(self):
        assert_raises(toolkit.Invalid,
            validators.deposited_dataset_curator_id, 'invalid', {})

    # Private datasets

    def test_always_false_if_not_sysadmin(self):
        normal_user = self.normal_user['name']
        sysadmin_user = self.sysadmin['name']
        tests = [
            # User, value provided, value expected
            (normal_user, True, False),
            (normal_user, False, False),
            (normal_user, None, False),
            (sysadmin_user, False, False),
            (sysadmin_user, True, True),
            (sysadmin_user, None, False),
        ]
        for test in tests:

            returned = validators.always_false_if_not_sysadmin(
                test[1], {'user': test[0]})
            assert_equals(
                returned,
                test[2],
                msg = 'User: {}, provided: {}, expected: {}, returned: {}'.format(
                    test[0], test[1], test[2], returned))


    def test_visibility_validator_restricted_false(self):
        tests = [
            ({'private': True, 'visibility': 'private'}, True),
            ({'private': False, 'visibility': 'private'}, True),
            ({'private': True, 'visibility': 'restricted'}, False),
            ({'private': False, 'visibility': 'restricted'}, False),
            ({'private': True, 'visibility': 'public'}, False),
            ({'private': False, 'visibility': 'public'}, False),
        ]
        for test in tests:
            key = ('visibility',)
            data = df.flatten_dict(test[0])
            validators.visibility_validator(key, data, {}, {})
            assert_equals(
                data[('private',)],
                test[1],
                msg = 'Data: {}, expected: {}, returned: {}'.format(
                    test[0], test[1], data[('private',)]))

    def test_visibility_validator_invalid_value(self):
        key = ('visibility',)
        data = {'private': True, 'visibility': 'unknown'}
        data = df.flatten_dict(data)
        assert_raises(
            toolkit.Invalid,
            validators.visibility_validator, key, data, {}, {})

    def test_visibility_validator_set_correct_value(self):
        tests = [
            ({'visibility': 'private'}, 'restricted'),
            ({'visibility': 'restricted'}, 'restricted'),
            ({'visibility': 'public'}, 'public'),
        ]
        for test in tests:
            key = ('visibility',)
            data = df.flatten_dict(test[0])
            validators.visibility_validator(key, data, {}, {})
            assert_equals(
                data[('visibility',)],
                test[1],
                msg = 'Data: {}, expected: {}, returned: {}'.format(
                    test[0], test[1], data[('private',)]))
