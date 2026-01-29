# Use the official Python image
FROM python:3.12-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.8.2  \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/project/src" \
    VENV_PATH="/opt/project/src/.venv"

# Prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Install system dependencies
RUN apt-get update \
    && apt-get install -y build-essential gettext curl \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSL https://install.python-poetry.org | python3 -

# Create appuser
RUN addgroup --gid 1024 appuser \
    && adduser --disabled-password --gecos "" --force-badname --ingroup appuser appuser

# Set WORKDIR
WORKDIR /opt/project/src

# Copy pyproject.toml first (for better caching)
COPY --chown=appuser:appuser ./src/pyproject.toml /opt/project/src/

# Create project directory and set permissions
RUN mkdir -p /opt/project/src \
    && chown -R appuser:appuser /opt/project

# Switch to non-root user for Poetry operations
USER appuser

# Configure Poetry
RUN poetry config virtualenvs.create true \
    && poetry config virtualenvs.in-project true

# Accept build argument to determine environment
ARG ENVIRONMENT=development

# Install dependencies
RUN poetry install --no-root

# Copy the rest of the application code
COPY --chown=appuser:appuser ./src /opt/project/src

# Switch back to root for system operations
USER root

# Copy entrypoint
COPY --chown=appuser:appuser ./docker/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint \
    && chmod +x /entrypoint

# Install gosu for step-down from root
RUN apt-get update && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/* \
    && gosu nobody true

WORKDIR /opt/project/src
ENTRYPOINT ["/entrypoint"]
