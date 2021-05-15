import datetime
import enum
import json
import random
import json
import uuid
from pathlib import Path
from typing import NoReturn, Optional, Sequence, TextIO

import yaml
from elasticsearch import Elasticsearch
from pydantic import BaseModel


HERE = Path(__file__).parent
ROOT = (HERE / '..').resolve()
MAPPINGS_DIRECTORY = ROOT / 'mappings'


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
