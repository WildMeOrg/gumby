# Expose the major parts of the elasticsearch library
from elasticsearch import Elasticsearch as Client

# Expose gumby's internals
from . import dsl
from .factories import *
from .models import *
