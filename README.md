# FastAPI Skeleton

A layered FastAPI project skeleton with presentation, business logic, and model layers.

## Running the app

```bash
docker compose up
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## Running the tests

Tests use SQLite in-memory — no database required.

```bash
# Create and activate the virtual environment (first time only)
python3 -m venv .venv
pip install -r requirements.txt

# Run all tests
.venv/bin/python -m pytest tests/ -v

# Run a specific layer
.venv/bin/python -m pytest tests/test_presentation/ -v
.venv/bin/python -m pytest tests/test_business/ -v
.venv/bin/python -m pytest tests/test_models/ -v
```

You can also run tests from VS Code via **Run & Debug > Run Tests** (`F5`).
