export GOOGLE_API_URL := "https://maps.dummy.com"
export GOOGLE_API_KEY := "dummy_key"
export DB_PORT := "5432"
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
    cd "{{ justfile_directory() }}" && poetry run python -m pytest tests -m wip -vv

# Run formatting
format:
    cd "{{ justfile_directory() }}" && \
      poetry run ruff format . && \
      poetry run ruff check . --fix --select I --select F401

# Lint
lint:
    cd "{{ justfile_directory() }}" && \
      poetry run ruff format --check . && \
      poetry run ruff check . && \
      poetry run mypy .

pytest +args="":
    export DB_HOST="{{ local_db_host }}" && \
    export DB_USER="{{ local_db_user }}" && \
    export DB_PASS="{{ local_db_pass }}" && \
    export DB_NAME="{{ local_db_name }}" && \
    poetry run python -m pytest {{args}}

pytest-verbose:
    export DB_HOST="{{ local_db_host }}" && \
    export DB_USER="{{ local_db_user }}" && \
    export DB_PASS="{{ local_db_pass }}" && \
    export DB_NAME="{{ local_db_name }}" && \
    poetry run python -m pytest -vvv

test: clean format lint coverage

coverage:
    export DB_HOST="{{ local_db_host }}" && \
    export DB_USER="{{ local_db_user }}" && \
    export DB_PASS="{{ local_db_pass }}" && \
    export DB_NAME="{{ local_db_name }}" && \
    poetry run coverage run -m pytest tests && \
    poetry run coverage report && \
    poetry run coverage html

coverage_report:
    poetry run coverage html

# Install deps
install:
    cd "{{ justfile_directory() }}" && poetry install --no-interaction --no-root

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
      poetry run python -m alembic current

db-upgrade:
    cd "{{ justfile_directory() }}" && \
      PYTHONPATH={{ justfile_directory() }} \
        export DB_HOST="{{ local_db_host }}" && \
        export DB_USER="{{ local_db_user }}" && \
        export DB_PASS="{{ local_db_pass }}" && \
        export DB_NAME="{{ local_db_name }}" && \
        echo "DB_USER: $DB_USER, DB_HOST: $DB_HOST, DB_NAME: $DB_NAME" && \
        poetry run python -m alembic upgrade head

# Downgrade to the specified database migration
db-downgrade revision:
    cd "{{ justfile_directory() }}" && \
      PYTHONPATH={{ justfile_directory() }} \
      poetry run python -m alembic downgrade {{ revision }}

# Downgrade to the specified database migration
db-new-migration name:
    cd "{{ justfile_directory() }}" && \
      PYTHONPATH={{ justfile_directory() }} \
      poetry run python -m alembic revision -m "{{ name }}"


run_api:
    cd "{{ justfile_directory() }}" && \
      PYTHONPATH={{ justfile_directory() }} \
        export DB_HOST="{{ local_db_host }}" && \
        export DB_USER="{{ local_db_user }}" && \
        export DB_PASS="{{ local_db_pass }}" && \
        export DB_NAME="{{ local_db_name }}" && \
        poetry run python api/main.py