import sys
import importlib.util
import json
from pathlib import Path

from elasticsearch.serializer import JSONSerializer
from invoke import task

from gumby import (
    Client,
    load_individuals_index_with_random_data,
    Individual,
)


@task
def init(c):
    """Initialize the elasticsearch instance"""
    client = Client()

    if Individual._index.exists(using=client):
        # XXX Just to ensure a clean slate each run =)
        Individual._index.delete(using=client)
    Individual.init(using=client)


@task
def load_random_data(c):
    """Loads random data into elasticsearch"""
    client = Client()
    load_individuals_index_with_random_data(client)


@task
def load_from_json(c, file):
    client = Client()

    with Path(file).open('r') as fb:
        data = json.load(fb)

    # Load as objects
    indvs = [Individual(**props) for props in data]

    # Persist the items
    last_item_idx = len(indvs) - 1
    for i, indv in enumerate(indvs):
        indv.save(using=client)

    # Refresh to ensure all shards are up-to-date and ready for requests
    Individual._index.refresh(using=client)


def _import_migration_func(script):
    """Imports a `migrate` function from an arbitrary filepath, given as `script`"""
    _script = Path(script)
    spec = importlib.util.spec_from_file_location('migration', _script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.migrate


@task
def run_migration(c, script):
    """Run a given migration script.
    This imports a `migrate` function from the script file.
    The documents in elasticsearch are iteratively given
    to this migration function.

    The intended use of this is to allow the user
    to preserve the existing document data,
    but modify it as needed.
    The primary usecase is for test data,
    because actual data should be rebuilt from source.

    """
    migration_func = _import_migration_func(script)
    client = Client()

    # Query all documents
    resp = Individual.search(using=client).execute()

    for doc in resp.hits:
        migration_func(doc)
        doc.save(using=client)

    # Refresh to ensure all shards are up-to-date and ready for requests
    Individual._index.refresh(using=client)


@task
def dump_index(c):
    """Dump index as JSON to stdout"""
    client = Client()

    resp = Individual.search(using=client).execute()
    print(JSONSerializer().dumps([hit.to_dict() for hit in resp.hits]))
