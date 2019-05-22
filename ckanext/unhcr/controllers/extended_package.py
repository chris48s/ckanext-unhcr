import logging
from ckan import model
import ckan.plugins.toolkit as toolkit
from ckan.controllers.package import PackageController
from ckanext.scheming.helpers import scheming_get_dataset_schema
log = logging.getLogger(__name__)


class ExtendedPackageController(PackageController):

    def copy(self, id):
        context = {'model': model, 'user': toolkit.c.user}

        # Get organizations
        orgs = toolkit.get_action('organization_list_for_user')(
            context, {'permission': 'package_create'})
        org_ids = [org['id'] for org in orgs]

        # Check access
        if not orgs:
            message = 'Not authorized to copy dataset "%s"'
            return toolkit.abort(403, message % id)

        # Get dataset
        try:
            dataset = toolkit.get_action('package_show')(context, {'id': id})
        except (toolkit.NotAuthorized, toolkit.ObjectNotFound):
            message = 'Not found py dataset "%s"'
            return toolkit.abort(404, message % id)

        # Extract data
        data = {}
        schema = scheming_get_dataset_schema('dataset')
        for field in schema['dataset_fields']:
            # We skip name/title
            if field['field_name'] in ['name', 'title']:
                continue
            # We skip autogenerated fields
            if field.get('form_snippet', True) is None:
                continue
            # We skip empty fields
            if field['field_name'] not in dataset:
                continue
            data[field['field_name']] = dataset[field['field_name']]
        data['type'] = 'dataset'
        data['private'] = bool(dataset.get('private'))
        if data.get('owner_org'):
            data['owner_org'] = data['owner_org'] if data['owner_org'] in org_ids else None
        data['original_dataset'] = dataset

        return self.new(data=data)

    def resource_copy(self, id, resource_id):
        context = {'model': model, 'user': toolkit.c.user}

        # Check access
        try:
            toolkit.check_access('package_update', context, {'id': id})
        except toolkit.NotAuthorized:
            message = 'Not authorized to copy resource of dataset "%s"'
            return toolkit.abort(403, message % id)

        # Get resource
        try:
            resource = toolkit.get_action('resource_show')(context, {'id': resource_id})
        except (toolkit.NotAuthorized, toolkit.ObjectNotFound):
            message = 'Not found resource "%s" of dataset "%s"'
            return toolkit.abort(404, message % (resource_id, id))

        # Extract data
        data = {}
        schema = scheming_get_dataset_schema('dataset')
        for field in schema['resource_fields']:
            # We skip url field (current file)
            if field['field_name'] == 'url':
                continue
            # We skip autogenerated fields
            if field.get('form_snippet', True) is None:
                continue
            if field['field_name'] in resource:
                data[field['field_name']] = resource[field['field_name']]
        data['name'] = '%s (copy)' % resource.get('name')

        return self.new_resource(id, data=data)
