from invoke import task

from gumby import initialize_indices


@task
def init(c):
    """Initialize the elasticsearch instance"""
    initialize_indices()


@task
def load_random_data(c):
    """Loads random data into elasticsearch"""
