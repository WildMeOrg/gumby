import datetime
import enum
import json
import random
import uuid
from pathlib import Path
from typing import NoReturn, Optional, Sequence, TextIO

import yaml
from elasticsearch import Elasticsearch
from pydantic import BaseModel


HERE = Path(__file__).parent
MAPPINGS_DIRECTORY = HERE / 'mappings'


# ############################################################################
# Index initialization

def _yml2json(yml: str) -> str:
    """converts YAML to JSON"""
    return json.dumps(
        yaml.load(yml, Loader=yaml.FullLoader),
        indent=4,
    )


INDEX_MAPPINGS = {
    # index-name : mapping JSON
    'individuals': _yml2json((MAPPINGS_DIRECTORY / 'individuals.yml').open('r').read()),
}


def initialize_indices() -> NoReturn:
    """Initializes the elasticsearch indices for this project"""
    es = Elasticsearch()
    for idx, mapping in INDEX_MAPPINGS.items():
        if es.indices.exists(index=idx):
            # XXX Just to ensure a clean slate each run =)
            es.indices.delete(index=idx)

        if not es.indices.exists(index=idx):
            es.indices.create(index=idx)
            es.indices.put_mapping(mapping, index=idx)


# ############################################################################
# Models

# FFF Ported from Python >=3.10
class StrEnum(str, enum.Enum):
    """
    Enum where members are also (and must be) strings
    """

    def __new__(cls, *values):
        if len(values) > 3:
            raise TypeError('too many arguments for str(): %r' % (values, ))
        if len(values) == 1:
            # it must be a string
            if not isinstance(values[0], str):
                raise TypeError('%r is not a string' % (values[0], ))
        if len(values) >= 2:
            # check that encoding argument is a string
            if not isinstance(values[1], str):
                raise TypeError('encoding must be a string, not %r' % (values[1], ))
        if len(values) == 3:
            # check that errors argument is a string
            if not isinstance(values[2], str):
                raise TypeError('errors must be a string, not %r' % (values[2]))
        value = str(*values)
        member = str.__new__(cls, value)
        member._value_ = value
        return member

    __str__ = str.__str__

    def _generate_next_value_(name, start, count, last_values):
        """
        Return the lower-cased version of the member name.
        """
        return name.lower()


class Sex(StrEnum):
    unknown = enum.auto()
    non_binary = 'non-binary'
    female = enum.auto()
    male = enum.auto()


class GeoPoint(BaseModel):
    lat: Optional[float]
    lon: Optional[float]


class Encounter(BaseModel):
    id: uuid.UUID
    point: GeoPoint
    animate_status: Optional[str]
    sex: Optional[Sex]
    submitter_id: str
    date_occurred: datetime.datetime


class Individual(BaseModel):
    # TODO producde the model schema from the ES doc mapping
    id: uuid.UUID
    name: str
    alias: str
    genus: Optional[str]
    species: Optional[str]
    last_sighting: datetime.datetime
    sex: Optional[Sex]
    # Not plural for ES convensions
    encounter: Sequence[Encounter]


# ############################################################################
# Randomizing object factories


SEXES = [x for x in Sex] + [None]
SUBMITTERS = ['julia', 'alice', 'henry', 'josh', 'fen', 'margo', 'kady', 'penny', 'eliot', 'quentin']
ALIASES = ['destiny', 'amanda', 'brook', 'alex', 'zoe', 'naomi', 'rick']
BINOMIAL_NOMENCLATURES = {
    # <genus>: [<species>, ...]
    'balaenoptera': ['acutorostrata', 'borealis', 'brydei', 'edeni', 'musculus', 'physalus'],
}


def random_date_delta():
    # Somewhere between one day and 2 years
    return datetime.timedelta(days=random.randint(1, 365 * 2))


def random_scientific_name_parts():
    genus = random.choice(list(BINOMIAL_NOMENCLATURES))
    species = random.choice(BINOMIAL_NOMENCLATURES[genus])
    return genus, species


def make_individual(**kwargs):
    """Produce a random individual documents with encounters"""
    genus, species = random_scientific_name_parts()
    props = {
        'id': uuid.uuid4(),
        'name': f'TI-{random.randint(0,99999):05}',
        'alias': random.choice(ALIASES),
        'genus': genus,
        'species': species,
        # 'last_sighting': datetime.datetime.now() - random_date_delta(),
        'sex': random.choice(SEXES),
        'encounter': [],
    }

    # ??? I'm just not sure we need to index the lastest-sighting separately.
    #     This may be redundant since we have the value in in the nested encounters.
    #     An aggregate in the query would probably work to provide this bit of data.
    # Determine the last_sighting value
    encounters = kwargs.get('encounter', [])
    try:
        latest_encounter = sorted(encounters, key=lambda x: x.date_occurred, reverse=True)[0]
    except IndexError:
        last_sighting = None
    else:
        last_sighting = latest_encounter.date_occurred
    finally:
        props['last_sighting'] = last_sighting

    return Individual(**(props | kwargs))


def make_encounter(**kwargs):
    random_central_geo_point = GeoPoint(
        lat=random.randint(-90 * 10**6, 90 * 10**6) * 10**-6,
        lon=random.randint(-180 * 10**6, 180 * 10**6) * 10**-6,
    )
    props = {
        'id': uuid.uuid4(),
        'point': GeoPoint(
            # TODO scatter slightly away from the central point
            lat=random_central_geo_point.lat,
            lon=random_central_geo_point.lon,
        ),
        'animate_status': None,
        'sex': random.choice(SEXES),
        'submitter_id': random.choice(SUBMITTERS),
        'date_occurred': datetime.datetime.now() - random_date_delta(),
    }

    return Encounter(**(props | kwargs))


def load_individuals_index_with_random_data():
    """Load the individuals index with data"""
    es = Elasticsearch()
    idx = 'individuals'

    for i in range(0, 50):
        encounters = [make_encounter() for i in range(0, random.randint(1, 20))]
        indv = make_individual(encounter=encounters)
        res = es.index(index=idx, body=indv.dict())
