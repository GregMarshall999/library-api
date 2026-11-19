# tests

pytest                    # run tests
pytest --cov=app          # same, plus a coverage table
ruff check .              # expect: All checks passed!
ruff format .             # auto-formats the code
mypy app                  # expect: Success: no issues found

# app

uvicorn app.main:app --reload