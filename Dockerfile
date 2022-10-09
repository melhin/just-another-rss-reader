FROM python:3.10

LABEL org.opencontainers.image.source=https://github.com/melhin/just-another-rss-reader

ARG APP_NAME=just-another-rss-reader
ARG APP_PATH=/opt/$APP_NAME
ARG PYTHON_VERSION=3.10.0
ARG POETRY_VERSION=1.1.13
ENV PYTHONPATH '${PYTHONPATH}:./src'

EXPOSE 7000

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 
ENV \
    POETRY_VERSION=$POETRY_VERSION \
    POETRY_NO_INTERACTION=1
ENV LANG C.UTF-8

# install deps
RUN apt-get update -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/

# Install Poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN pip install -U pip setuptools wheel poetry
ENV PATH="$POETRY_HOME/bin:$PATH;"


WORKDIR /
RUN poetry config virtualenvs.create false
COPY ./poetry.lock ./pyproject.toml ./

RUN poetry install --only main
# loading language models
RUN python -m spacy download en_core_web_sm
RUN python -m nltk.downloader punkt

COPY ./src ./src
COPY ./alembic ./alembic
COPY ./run.py ./collect.py ./alembic.ini ./docker-entrypoint.sh ./

ENTRYPOINT [ "bash", "docker-entrypoint.sh" ]
CMD ["app"]
