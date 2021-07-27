from os import getenv

# Expose the major parts of the elasticsearch library
from elasticsearch import Elasticsearch as BaseClient

# Expose gumby's internals
from . import dsl
from .factories import *
from .models import *


class Client(BaseClient):
    def __init__(self, hosts=None, **kwargs):
        if not hosts:
            hosts = getenv('ELASTICSEARCH_HOSTS', '').split(',')
        super().__init__(hosts=hosts, **kwargs)
