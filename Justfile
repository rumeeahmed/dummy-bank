local_db_host := "127.0.0.1"
local_db_user := "service"
local_db_pass := "service"
local_db_name := "service"

# this help screen
show_help:
    @just --list

clean:
    find . -type d -name __pycache__ -exec rm -r {} \+

wip:
    cd "{{ justfile_directory() }}" && uv run python -m pytest tests -m wip -vv

# Run formatting
format:
    cd "{{ justfile_directory() }}" && \
      uv run ruff format . && \
      uv run ruff check . --fix --select I --select F401

# Lint
lint:
    cd "{{ justfile_directory() }}" && \
      uv run ruff format --check . && \
      uv run ruff check . && \
      uv run ty check .

pytest +args="":
    uv run python -m pytest {{args}}

pytest-parallel workers="auto" +args="":
    uv run python -m pytest -n {{workers}} --dist loadscope {{args}}

pytest-verbose:
    uv run python -m pytest -vvv

test: clean format lint coverage-parallel

coverage:
    uv run coverage run -m pytest tests && \
    uv run coverage report && \
    uv run coverage html

coverage-parallel workers="auto" +args="":
    uv run python -m pytest \
        -n {{workers}} \
        --cov=src/dummy_bank \
        --cov-report=term \
        --cov-report=html \
        --cov-fail-under=100 \
        {{args}}

coverage_report:
    uv run coverage html

# Install deps
install:
    cd "{{ justfile_directory() }}" && uv sync

# Run postgres
up:
    docker-compose up -d

# Stop postgres
down:
    docker-compose stop && docker-compose rm -f

# Check database migration
db-version:
    cd "{{ justfile_directory() }}" && \
      PYTHONPATH={{ justfile_directory() }} \
      uv run python -m alembic current

db-upgrade:
    cd "{{ justfile_directory() }}" && \
      PYTHONPATH={{ justfile_directory() }} \
        export DB_HOST="{{ local_db_host }}" && \
        export DB_USER="{{ local_db_user }}" && \
        export DB_PASS="{{ local_db_pass }}" && \
        export DB_NAME="{{ local_db_name }}" && \
        echo "DB_USER: $DB_USER, DB_HOST: $DB_HOST, DB_NAME: $DB_NAME" && \
        uv run python -m alembic upgrade head

# Downgrade to the specified database migration
db-downgrade revision:
    cd "{{ justfile_directory() }}" && \
      PYTHONPATH={{ justfile_directory() }} \
      uv run python -m alembic downgrade {{ revision }}

# Downgrade to the specified database migration
db-new-migration name:
    cd "{{ justfile_directory() }}" && \
      PYTHONPATH={{ justfile_directory() }} \
      uv run python -m alembic revision -m "{{ name }}"


run_api:
    cd "{{ justfile_directory() }}" && \
      PYTHONPATH={{ justfile_directory() }} \
        uv run python api/main.py
