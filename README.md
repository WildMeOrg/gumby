# CODEX - Search Index


The service used to search within CODEX. This search index is comprised of a number of indexes used [by the backend]() as well as by the [codex-frontend]().

This project is a part of [CODEX]().

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

## Usage

### Loading Random Data

To load random data into the instance use the following command:

```bash
invoke load-random-data
```

## License

This software is subject to the provisions of Apache License Version 2.0 (APL). See `LICENSE` for details. Copyright (c) 2021 Wild Me
