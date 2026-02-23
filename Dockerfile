FROM python:3.13-slim

# Build-time environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_CACHE_DIR='/tmp/poetry_cache'

# Install Git
RUN apt-get update && \
    apt-get install -y git procps wget && \
    rm -rf /var/lib/apt/lists/*

# Bake the Git config into the image
RUN git config --global user.email "agent@antigravity.local" && \
    git config --global user.name "Antigravity Agent" && \
    git config --global --add safe.directory /app

# Install Poetry
RUN pip install --no-cache-dir poetry

WORKDIR /app

# Install ONLY dependencies (The Cached Layer)
COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-interaction --no-root && rm -rf $POETRY_CACHE_DIR

# Copy the actual code
COPY . /app/

# Fast install of the local package itself
RUN poetry install --no-interaction

# Install pre-commit hooks
RUN poetry run pre-commit install

CMD ["/bin/bash"]
