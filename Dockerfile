FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl build-essential
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:${PATH}"

COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY . /app

CMD ["python", "experiment.py"]
