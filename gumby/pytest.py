"""Test the individuals index"""
import json
import os
import time
from pathlib import Path

import pytest
from elasticsearch_dsl import Q

from gumby import Client
from gumby.factories import make_encounter, make_individual
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
def gumby_faux_index_data(request, gumby_client):
    # Set up index (and cleanup before if necessary)
    if Individual._index.exists(using=gumby_client):
        Individual._index.delete(using=gumby_client)
    Individual.init(using=gumby_client)
    # Register teardown
    request.addfinalizer(lambda: Individual._index.delete(using=gumby_client))

    # Load data from file
    with RAW_INDIVIDUALS_DUMP.open('r') as fb:
        raw_data = json.load(fb)

    # Load as objects
    indvs = [Individual(**props) for props in raw_data]

    # Persist the items
    last_item_idx = len(indvs) - 1
    for i, indv in enumerate(indvs):
        indv.save(using=gumby_client)

    # Refresh to ensure all shards are up-to-date and ready for requests
    Individual._index.refresh(using=gumby_client)

    return {Individual: indvs}
