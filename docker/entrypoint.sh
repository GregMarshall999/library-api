#!/bin/sh
# Runs before the main command: bring the database schema up to date, then start the app.
set -e

echo "Applying database migrations..."
alembic upgrade head

# exec replaces this shell with the CMD (uvicorn), so it receives stop signals directly.
exec "$@"