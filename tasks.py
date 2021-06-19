import sys

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
    load_individuals_index_with_random_data()


@task
def dump_index(c):
    """Dump index as JSON to stdout"""
    client = Client()

    resp = Individual.search(using=client).execute()
    print(JSONSerializer().dumps([hit.to_dict() for hit in resp.hits]))
