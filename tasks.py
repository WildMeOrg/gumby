from elasticsearch import Elasticsearch
from invoke import task

from gumby import (
    load_individuals_index_with_random_data,
    Individual,
)


@task
def init(c):
    """Initialize the elasticsearch instance"""
    client = Elasticsearch()

    if Individual._index.exists(using=client):
        # XXX Just to ensure a clean slate each run =)
        Individual._index.delete(using=client)
    Individual.init(using=client)


@task
def load_random_data(c):
    """Loads random data into elasticsearch"""
    load_individuals_index_with_random_data()
