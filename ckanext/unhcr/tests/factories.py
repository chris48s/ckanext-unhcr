from ckan.tests import factories


class DataContainer(factories.Organization):

    type = 'data-container'
    country = ['SVN']
    geographic_area = 'southern_africa'


class Dataset(factories.Dataset):

    unit_of_measurement = 'individual'
    keywords = ['3', '4']
    archived = 'False'
    data_collector = 'ACF,UNHCR'
    data_collection_technique = 'f2f'
    sampling_procedure = 'nonprobability'
    operational_purpose_of_data = 'cartography'
    visibility = 'public'
    external_access_level = 'open_access'


class Resource(factories.Resource):

    type = 'data'
    file_type = 'microdata'
    identifiability = 'anonymized_public'
    date_range_start = '2018-01-01'
    date_range_end = '2019-01-01'
    process_status = 'anonymized'
    version = '1'


class DepositedDataset(factories.Dataset):

    type = 'deposited-dataset'
    owner_org = 'id-data-deposit'
    owner_org_dest = 'id-data-target'
    visibility = 'public'
