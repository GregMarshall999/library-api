# init

source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"

# tests

pytest
pytest --cov=app --cov-report=term-missing
ruff check .
ruff format .
mypy app tests

# app

uvicorn app.main:app --reload