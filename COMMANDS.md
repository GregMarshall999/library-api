# init

source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"

# alembic migrations

alembic init migrations
alembic revision --autogenerate -m "revision name"
alembic upgrade head

# tests

pytest
pytest --cov=app --cov-report=term-missing
ruff check .
ruff format .
mypy app tests

# app

uvicorn app.main:app --reload