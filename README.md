# Codex - Search Index


The service used to search within Codex. This search index is comprised of a number of indexes used [by the backend]() as well as by the [codex-frontend]().

This project is a part of [Wild Me Codex]().


## Install

This assumes you have [Docker](https://docker.io) installed.
This assumes you have [Python](https://python.org) >= 3.9 installed.
You should also use a [python virtual environment](https://docs.python.org/dev/library/venv.html).

Run the following commands:

```bash
docker compose up -d
pip install -r requirements.txt
invoke init
```

This will run the [ELK stack](https://www.elastic.co/what-is/elk-stack) in the background.

- [elasticsearch http://localhost:9200](http://localhost:9200)
- [kibana http://localhost:5601](http://localhost:5601)

The `invoke init` command initializes the elasticserach instance with our indexes.


## Testing

Run the tests use `pytest` on the commandline (installation is a prerequisite).

The tests will create new indices that are prefixed with `test-`.
These should be cleaned up automatically after each run,
but there is no harm if they are not cleaned up.

#### The point of these tests...

The tests attempt to exercise common queries.
In these tests we are effectively ensuring that any breaking changes
to an [index's _mapping_](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html)
(see models which define the mappings) are caught and addressed.

#### Why test here rather than in Houston (or other Codex services)?

These are very basic tests that simply ensure the data structures (aka indices) defined here are sound before other services attempt to use them.

It should be possible to benchmark changes to this service outside the scope of other services.

Also, these tests to not negate integration testing with this service from Houston.
It do however mean that unit-testing can be done here rather in services using this service.


## Usage

### Loading Random Data

To load random data into the instance use the following command:

```bash
invoke gumby.init
invoke gumby.load-random-data
```

### Dumping an Index to JSON

This shouldn't be done with production data or used as a backup. See elasticsearch's `_snapshot` documentation for a possible better way of working with production data. This functionality is mostly for development and testing; and it may be removed in the future.

To dump the index to a JSON file:

```bash
invoke dump-index | python -m json.tool > individuals.json
```

The data in this example is piped to python's `json.tool` for multiline pretty-printing to file, which makes the data easier to understand when committing the changes.

### Loading an Index from JSON

To load the index from a JSON file:

```bash
invoke load-from-json individuals.json
```

### Create and Run a Migration

Note, this functionality should not be used for production under any circumstance. This is purely implemented for development and testing. The goal is to maintain the randomly generated record so that all the tests that rely on it don't completely break on a change.

To create a migration, create a script (see `_migrations` directory for examples). The script must have a `migrate` function that takes a single argument, `doc`, that is the document object.

The migration process essentially iterates over each document in an index, feeding that to the given migration, and saving it.

To run a migration:

```bash
invoke run-migration _migrations/0001-bday_party.py
```


## License

This software is subject to the provisions of Apache License Version 2.0 (APL). See `LICENSE` for details. Copyright (c) 2021 Wild Me
