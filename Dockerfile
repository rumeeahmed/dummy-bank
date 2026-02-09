# syntax=docker/dockerfile:1
# Keep this syntax directive! It's used to enable Docker BuildKit

################################
# PYTHON-BASE
# Sets up all our shared environment variables
################################
FROM python:3.14-slim as python-base

# python
ENV PYTHONUNBUFFERED=1 \
  # prevents python creating .pyc files
  PYTHONDONTWRITEBYTECODE=1 \
  \
  # pip
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  \
  # uv
  UV_LINK_MODE=copy \
  \
  # paths
  # this is where our requirements + virtual environment will live
  PYSETUP_PATH="/opt/pysetup" \
  VENV_PATH="/opt/pysetup/.venv"


# prepend uv and venv to path
ENV PATH="/root/.local/bin:$VENV_PATH/bin:$PATH"


################################
# BUILDER-BASE
# Used to build deps + create our virtual environment
################################
FROM python-base as builder-base

RUN apt-get update \
  && apt-get install --no-install-recommends -y \
  # deps for installing uv
  curl \
  # deps for building python deps
  build-essential \
  && rm -rf /var/lib/apt/lists/*

# Install uv
RUN --mount=type=cache,target=/root/.cache \
  curl -LsSf https://astral.sh/uv/install.sh | sh

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY pyproject.toml ./

# install runtime deps into project-local .venv
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --no-dev --no-install-project


################################
# PRODUCTION
# Final image used for runtime
################################
FROM python-base as production
ENV FASTAPI_ENV=production
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY . /app/
WORKDIR /app

EXPOSE 8080
ENV PYTHONPATH="/app"
CMD ["python", "-m", "api.main"]
