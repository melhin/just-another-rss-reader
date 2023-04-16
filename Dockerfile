FROM python:3.10.1

LABEL org.opencontainers.image.source=https://github.com/melhin/just-another-rss-reader

ARG APP_NAME=just-another-rss-reader
ARG APP_PATH=/opt/$APP_NAME
ARG PYTHON_VERSION=3.10.1
ARG POETRY_VERSION=1.1.13

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


WORKDIR /reader
RUN poetry config virtualenvs.create false
COPY ./poetry.lock ./pyproject.toml ./

RUN poetry install --only main
# loading language models
RUN python -m spacy download en_core_web_sm
RUN python -m nltk.downloader punkt

ENV PYTHONPATH '${PYTHONPATH}:./src'
COPY src src
COPY alembic alembic
COPY run.py collect.py alembic.ini docker-entrypoint.sh /reader/

ENTRYPOINT [ "/reader/docker-entrypoint.sh" ]
CMD ["app"]
