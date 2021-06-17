# Expose the major parts of the elasticsearch library
from elasticsearch import Elasticsearch as Client

# Make the DSL interface importable as 'dsl'
import elasticsearch_dsl as dsl

# Expose gumby's internals
from .factories import *
from .models import *
