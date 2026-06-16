FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock* ./
COPY src ./src
COPY tests ./tests

RUN pip install uv && uv sync --extra dev

CMD ["uv", "run", "uvicorn", "deriv_organismo.main:app", "--host", "0.0.0.0", "--port", "8000"]
