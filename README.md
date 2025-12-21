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

## Strategy to reach the project goals

This project aims to track player knowledge during a game of Clue/Cluedo and predict the correct solution. The most effective path is to build a reliable data model first, then layer the inference engine and API workflows on top of it, and finally harden the system with tests and deployment tooling.

1. **Define the domain model up front**  
   Model the game in terms of players, cards, hands, suggestions, showings, and the hidden envelope. Replace the placeholder `Post`/`Vote` models and generate Alembic migrations. This establishes the data backbone for everything else.
2. **Capture authoritative game events**  
   Build endpoints that record immutable facts: game creation, player order, dealt cards, suggestions, and which player showed (if any). These events are the input to all inference logic, so treat them as the source of truth.
3. **Implement deterministic inference first**  
   Start with rule-based deductions (e.g., if a player showed a card, they must have one of the suggested cards). Only after deterministic rules are solid should you add probability weighting.
4. **Expose the knowledge state via API**  
   Provide a read-only endpoint that returns current deductions and probabilities per card and per player. This becomes the main surface for clients or UI to consume.
5. **Secure and validate inputs**  
   Reuse OAuth2 utilities and add validation for game state transitions to prevent inconsistent data (e.g., no showing before a suggestion is logged).
6. **Test the inference engine rigorously**  
   Expand `pytest` coverage with unit tests for deduction rules and integration tests for common gameplay scenarios. This is the fastest way to ensure correctness as logic grows.
7. **Polish deployment once the core works**  
   After the logic is stable, tighten Docker and Compose configs, add environment configuration, and consider production hosting details.

## Contributing

This repository is currently experimental.  Feel free to open issues or pull requests with ideas or improvements.  As the project matures, contribution guidelines and a code of conduct will be added.
