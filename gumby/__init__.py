from os import getenv

# Expose the major parts of the elasticsearch library
from elasticsearch import Elasticsearch as BaseClient

# Expose gumby's internals
from . import dsl  # noqa
from .factories import *  # noqa
from .initialize import *  # noqa
from .models import *  # noqa


class Client(BaseClient):
    def __init__(self, hosts=None, http_auth=None, **kwargs):
        if not hosts:
            hosts = getenv('ELASTICSEARCH_HOSTS', '').split(',')
        if not http_auth:
            # Looking for a value like `<username>:<password>`
            http_auth = getenv('ELASTICSEARCH_HTTP_AUTH', None)
        super().__init__(hosts=hosts, http_auth=http_auth, **kwargs)
