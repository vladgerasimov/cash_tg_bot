FROM python:3.12

RUN pip install poetry
WORKDIR ./app

COPY bot/ ./bot/
COPY configs/ ./configs/
COPY core/ ./core/
COPY main.py ./main.py
COPY poetry.lock ./poetry.lock
COPY pyproject.toml ./pyproject.toml
COPY .env ./.env

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-cache --no-root

CMD poetry run python main.py