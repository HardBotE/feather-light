FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry
ENV POETRY_VIRTUALENVS_CREATE=false POETRY_NO_INTERACTION=1

COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root

RUN pip install --no-cache-dir uvicorn watchfiles

COPY . .

CMD ["python", "-m", "uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
