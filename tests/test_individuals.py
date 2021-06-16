"""Test the individuals index"""
import json
import time
from pathlib import Path

import pytest
from elasticsearch_dsl import Q

from gumby import Client
from gumby.factories import make_encounter, make_individual
from gumby.models import Individual


HERE = Path(__file__).parent

# Generated using `invoke dump-index | python -m json.tool > tests/individuals.json`
RAW_INDIVIDUALS_DUMP = HERE / 'individuals.json'


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def individuals(request, client):
    # Set up index (and cleanup before if necessary)
    if Individual._index.exists(using=client):
        Individual._index.delete(using=client)
    Individual.init(using=client)
    # Register teardown
    request.addfinalizer(lambda: Individual._index.delete(using=client))

    # Load data from file
    with RAW_INDIVIDUALS_DUMP.open('r') as fb:
        raw_data = json.load(fb)

    # Load as objects
    indvs = [Individual(**props) for props in raw_data]

    # Persist the items
    last_item_idx = len(indvs) - 1
    for i, indv in enumerate(indvs):
        indv.save(using=client)

    # Refresh to ensure all shards are up-to-date and ready for requests
    Individual._index.refresh(using=client)
    return indvs


class TestUserStories:
    """Testing user stories for specific actor's desires.

    As <actor>, I want <desire> [so that <benefit>].

    """

    @pytest.fixture(autouse=True)
    def set_up(self, client, individuals):
        self.client = client
        self.individuals = individuals

    def test_individual_by_encounter_scientific_name_and_annotation(self):
        """As a researcher I want to search for all Individuals that have encounters where the species is “Delphinapterus”, genus is “leucas” and are associated with at least one image (Annotation).

        """
        # Criteria
        query = Q(
            'bool',
            must=Q(
                'nested',
                path='encounters',
                query=Q(
                    'bool',
                    filter=[
                        Q('term', encounters__species='edeni'),
                        Q('term', encounters__genus='balaenoptera'),
                        Q('term', encounters__has_annotation=True),
                    ])
            )
        )

        s = Individual.search(using=self.client)
        assert len(s.execute()) == len(self.individuals)
        resp = s.query(query).execute()
        assert resp.hits.total.value == 7

    @pytest.mark.skip("not-implemented-yet")
    def test_individual_by_encounter_and_annotation_with_keyword(self):
        """As a researcher I want to find all Individuals that have at least one encounter that contains an annotation with the keyword “Medium Coat”.

        """
        # Note, by design individuals must have at least one encounter to be indexed.

        # Criteria
        query = Q(
            'bool',
            must=Q(
                'nested',
                path='encounters',
                query=Q(
                    'bool',
                    filter=(
                        Q('term', encounters__has_annotation=True)
                        # | Q('term', encounters__annotations__keyword='medium coat')
                    )
                )
            )
        )

        s = Individual.search(using=self.client)
        assert len(s.execute()) == len(self.individuals)
        resp = s.query(query).execute()
        assert resp.hits.total.value == 10


class TestQueries:
    """Test queries that are commonly used, complex, typically regress, etc."""

    def test(self):
        client = Client()

        # Initialize index
        if Individual._index.exists(using=client):
            Individual._index.delete(using=client)
        Individual.init(using=client)

        name = 'test-indv'
        # Load index
        indv = Individual(**(make_individual() | {'name': name}))
        indv.save(using=client, refresh='wait_for')

        # Query
        from elasticsearch_dsl import Search
        s = Search(using=client, index='individuals').query('match', name=name)
        resp = s.execute()
        assert resp.success()
        assert resp.hits.total.value == 1

        # Cleanup
        Individual._index.delete(using=client)


# ############################################################################
# Example queries
# ############################################################################

"""
GET individuals/_search
{
  "query": {
    "bool": {
      "filter": [
        { "term": { "sex": "female" } }
        ,{ "range": { "encounters.date_occurred": {"gte": "2021-04-25"} } }
      ]
    }
  }
}
"""


"""
{
  "query": {
    "bool": {
      "filter": [
        { "range": { "encounters.date_occurred": {"gte": "2020-04-25"} } }
      ]
    }
  }
}
"""


"""
# search for criteria in a nested encounter
GET individuals/_search
{
  "query": {
    "nested":{
      "path": "encounters",
      "query": {
        "bool": {
          "filter": { "match": { "encounters.sex": "female" } }
        }
      }
    }
  }
}
"""

"""
# search for multiple criteria in nested encounters
GET individuals/_search
{
  "query": {
    "nested":{
      "path": "encounters",
      "query": {
        "bool": {
          "filter": [
            { "term": { "encounters.sex": "female" } }
            ,{ "range": {"encounters.date_occurred": {"gte": "2021-05-01"}} }
            ,{ "term": {"encounters.submitter_id": "margo"} }
          ]
        }
      }
    }
  }
}
"""


"""
# search for individual by individual and nested encounter criteria
GET individuals/_search
{
  "query": {
    "bool": { 
      "must": [
        { "term": { "genus": "Balaenoptera" } }
        ,{"nested":{
          "path": "encounters",
          "query": {
            "bool": {
              "filter": [
                { "term": { "encounters.sex": "female" } }
                ,{ "range": {"encounters.date_occurred": {"gte": "2021-05-01"}} }
                ,{ "term": {"encounters.submitter_id": "margo"} }
              ]
            }
          }
        }}
      ]
    }
  }
}
"""
