# BTE-REST-API

This is a turnip.exchange scraping REST API built using FASTAPI that automates
the way users search for suitable islands on turnip.exchange.
This includes but is not limited to setting a price thresholds and island tip
requirements.

## Features

---
The following features are subject to change.

- Setting a turnip price threshold
- Setting description keywords to ignore islands
- Track islands that users have been notified
- Opens a new (chrome) tab for each suitable island

## Setup

---

```sh
make build
```

## Usage

---

1. ```sh
    make run
    ```

2. Open [http://0.0.0.0:8080/docs](http://0.0.0.0:8080/docs) in a browser.

3. Interact with the REST endpoints

## Teardown

---

```sh
make clean
```

## Docker

---

WIP will write a script to automate this

1. Build docker image
`docker build -t bte-rest-api .`

2. Run docker container
`docker-compose up`

3. Stop docker container
`docker-compose down`

## Tests

---

```sh
make dev
make test
```

