import json
from pathlib import Path
from typing import NoReturn, TextIO

import yaml
from elasticsearch import Elasticsearch


here = Path(__file__).parent
mappings_directory = here / 'mappings'


def _yml2json(yml: str) -> str:
    """converts YAML to JSON"""
    return json.dumps(
        yaml.load(yml, Loader=yaml.FullLoader),
        indent=4,
    )


index_mappings = {
    # index-name : mapping JSON
    'individuals': _yml2json((mappings_directory / 'individuals.yml').open('r').read()),
}


def initialize_indices() -> NoReturn:
    """Initializes the elasticsearch indices for this project"""
    es = Elasticsearch()
    for idx, mapping in index_mappings.items():
        # XXX Just to ensure a clean slate each run =)
        es.indices.delete(index=idx)

        if not es.indices.exists(index=idx):
            es.indices.create(index=idx)
            es.indices.put_mapping(mapping, index=idx)
