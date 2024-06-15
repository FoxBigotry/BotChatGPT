FROM python:3.11.6-slim as builder

RUN apt-get update && \
    pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install && \
    rm -rf $POETRY_CACHE_DIR

FROM python:3.11.6-slim as runtime

RUN apt-get update

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    IMAGEIO_FFMPEG_EXE=/usr/bin/ffmpeg

WORKDIR /app

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY . /app

CMD ["python", "start_bot.py"]
