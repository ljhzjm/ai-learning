#!/bin/sh
set -e
if [ "$#" -gt 0 ]; then exec "$@"; else alembic upgrade head; exec uvicorn w2d3_sqlalchemy_todo.main:app --host 0.0.0.0 --port 8000; fi