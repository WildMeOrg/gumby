from invoke import task

from gumby import (
    initialize_indices,
    load_individuals_index_with_random_data,
)


@task
def init(c):
    """Initialize the elasticsearch instance"""
    initialize_indices()


@task
def load_random_data(c):
    """Loads random data into elasticsearch"""
    load_individuals_index_with_random_data()
