# CODEX - Search Index


The service used to search within CODEX. This search index is comprised of a number of indexes used [by the backend]() as well as by the [codex-frontend]().

This project is a part of [CODEX]().

## Install

Assumes you have [Docker](https://docker.io) installed.

```bash
docker compose up -d
```

This will run the [ELK stack](https://www.elastic.co/what-is/elk-stack) in the background.

- [elasticsearch http://localhost:9200](http://localhost:9200)
- [kibana http://localhost:5601](http://localhost:5601)

## License

This software is subject to the provisions of Apache License Version 2.0 (APL). See `LICENSE` for details. Copyright (c) 2021 Wild Me
