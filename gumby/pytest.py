"""Test the individuals index"""
import json
import os
from pathlib import Path

import pytest

from gumby import Client
from gumby import dsl
from gumby.models import Individual


HERE = Path(__file__).parent

# Generated using `invoke dump-index | python -m json.tool > tests/individuals.json`
RAW_INDIVIDUALS_DUMP = HERE / 'testing-data/individuals.json'


@pytest.fixture
def gumby_client():
    hosts = os.getenv('ELASTICSEARCH_HOSTS')
    if not hosts:
        # ensure the default
        hosts = None
    else:
        hosts = [h.strip() for h in hosts.split(',')]
    return Client(hosts)


@pytest.fixture
def gumby_individual_index_name():
    return f'test-{Individual.Index.name}'


@pytest.fixture
def gumby_faux_index_data(request, gumby_client, gumby_individual_index_name):
    idx_name = gumby_individual_index_name
    idx = dsl.Index(name=idx_name, using=gumby_client)

    # Set up index (and cleanup before if necessary)
    # Use a bit of magic to let the custom named index know about
    # our document mapping as defined by the model.
    idx.get_or_create_mapping().update(Individual._doc_type.mapping)
    # Remove the index if it already exists
    if idx.exists():
        idx.delete()
    # Create the index with mapping
    idx.create()

    # Register teardown
    request.addfinalizer(idx.delete)

    # Load data from file
    with RAW_INDIVIDUALS_DUMP.open('r') as fb:
        raw_data = json.load(fb)

    # Load as objects
    indvs = [Individual(**props) for props in raw_data]

    # Persist the items
    for i, indv in enumerate(indvs):
        indv.save(index=idx_name, using=gumby_client)

    # Refresh to ensure all shards are up-to-date and ready for requests
    idx.refresh()

    return {Individual: indvs}
