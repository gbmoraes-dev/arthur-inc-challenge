FROM python:3.12-slim AS base

# ---------

FROM base AS deps

WORKDIR /app

COPY Pipfile Pipfile.lock ./

RUN pip install pipenv

RUN pipenv requirements > requirements.txt

RUN pip install -r requirements.txt

# ---------

FROM base AS runner

WORKDIR /app

ENV PYTHONUNBUFFERED=1

ENV PYTHONPATH=/app:/app/src

RUN addgroup --system --gid 1001 pythonapp

RUN adduser --system --uid 1001 appuser

RUN chown appuser:pythonapp .

COPY --chown=appuser:pythonapp . .

COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

ENV BRASIL_API_URL=https://brasilapi.com.br/api/cep/v2/

ENV OSRM_API_URL=http://router.project-osrm.org/route/v1/driving/

USER appuser

ENTRYPOINT ["python", "-m", "src.main"]
