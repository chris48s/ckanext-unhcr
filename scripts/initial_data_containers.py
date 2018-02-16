import csv
import ckanapi
from slugify import slugify

INPUT_CSV = 'initial_data_container_list_feb_2018.csv'

CKAN_API_KEY = 'XXXXXX'
ckan = ckanapi.RemoteCKAN('http://193.134.241.126', apikey=CKAN_API_KEY)

done = []
orgs = []

with open(INPUT_CSV, 'rb') as csv_file:
    reader = csv.reader(csv_file)
    # Skip headers
    next(reader, None)
    for row in reader:

        # Save root level containers
        if row[0] not in done:
            done.append(row[0])

            orgs.append({
                'name': slugify(row[0]),
                'title': row[0],
            })

        # Save 1st level containers
        if row[1].strip() and row[1] not in done:
            done.append(row[1])

            orgs.append({
                'name': slugify(row[1]),
                'title': row[1],
                'groups': [{'name': slugify(row[0])}],
            })

        # Save 2nd level containers
        if row[2].strip() and row[2] not in done:
            done.append(row[2])

            orgs.append({
                'name': slugify(row[2]),
                'title': row[2],
                'groups': [{'name': slugify(row[1])}],
            })

# Create orgs in CKAN
for org in orgs:
    try:
        ckan.action.organization_create(**org)
        print 'Created data container {}'.format(org['name'])
    except ckanapi.errors.ValidationError:
        pass
