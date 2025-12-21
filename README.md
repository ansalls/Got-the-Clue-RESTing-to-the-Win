# Got-the-Clue RESTing to the Win

This repository contains the starting point of a containerised web service powered by **FastAPI** and **PostgreSQL**.  The goal of the project is to track which player knows which cards during a game of Clue/Cluedo and to predict the correct solution.  In its current state the codebase is a generic REST template that provides user authentication, basic CRUD endpoints and automated tests.

## Current structure

```
app/                FastAPI application package
├── main.py         Application entry point
├── models.py       SQLAlchemy models (posts, users, votes)
├── routers/        API route handlers (auth, post, user, vote)
├── schemas.py      Pydantic schemas for request/response models
├── utils.py        Helper utilities
└── ...

alembic/            Database migrations
Dockerfile          Build recipe for the API container
docker-compose-dev.yml   Development stack with Postgres
docker-compose-prod.yml  Production stack example
nginx               Example reverse proxy configuration
```

Automated tests for the existing endpoints live in `tests/` and rely on `pytest`.
These tests run against a temporary SQLite database so no external PostgreSQL server is needed.

## Running locally

The quickest way to run the current service is with Docker Compose:

```bash
docker-compose -f docker-compose-dev.yml up --build
```

This will build the API image and start both the API and a Postgres instance.  The API will be available on `http://localhost:8000` with automatic reload enabled.

## Roadmap

The project is in a pre-alpha state.  Below is a high‑level set of tasks to transform the template into a Clue/Cluedo assistant.  These will be completed iteratively:

1. **Replace placeholder models** – Introduce domain models for players, cards, hands and suggestions instead of the example `Post`/`Vote` models.  Create migration scripts via Alembic.
2. **Game state API** – Add routes to
   - create a game and register players
   - record dealt cards
   - log suggestions and showings
   - expose an endpoint that returns current probability estimates for each card
3. **Knowledge engine** – Implement logic that analyses logged actions to infer which cards remain possible in the envelope.  This may start simple and later incorporate probability weights.
4. **Front‑end considerations** – Provide OpenAPI documentation (already enabled by FastAPI) and later design a lightweight UI or API clients.
5. **Authentication & authorisation** – Reuse the existing OAuth2 utilities to secure the endpoints so that only authorised players can record or view game information.
6. **Testing** – Extend the `pytest` suite with unit and integration tests for the new models and endpoints.  Continuous Integration can be set up later to run these automatically.
7. **Container & deployment** – Polish the Dockerfiles and `docker-compose` setups for production (including the provided `nginx` example).  Evaluate hosting options once the API stabilises.

## Contributing

This repository is currently experimental.  Feel free to open issues or pull requests with ideas or improvements.  As the project matures, contribution guidelines and a code of conduct will be added.

