"""Test the individuals index"""
import time

import pytest
from elasticsearch import Elasticsearch

from gumby.models import Individual



class TestUserStories:
    """Testing user stories for specific actor's desires.

    As <actor>, I want <desire> [so that <benefit>].

    """

    @pytest.mark.skip("not-implemented-yet")
    def test_individual_by_encounter_scientific_name_and_annotation(self):
        """As a researcher I want to search for all Individuals that have encounters where the species is “Delphinapterus”, genus is “leucas” and are associated with at least one image (Annotation).

        """
        pass

    @pytest.mark.skip("not-implemented-yet")
    def test_individual_by_encounter_and_annotation_with_keyword(self):
        """As a researcher I want to find all Individuals that have at least one encounter that contains an annotation with the keyword “Medium Coat”.

        """
        pass


class TestQueries:
    """Test queries that are commonly used, complex, typically regress, etc."""

    def test(self):
        client = Elasticsearch()

        # Initialize index
        # FIXME This initializes all indices, but we only need the 'individuals' index.
        #       And ideally the index should be named something like 'test-N-individuals',
        #       where N is a random number.
        if Individual._index.exists(using=client):
            Individual._index.delete(using=client)
        Individual.init(using=client)

        name = 'test-indv'
        # Load index
        from gumby.factories import make_encounter, make_individual
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
