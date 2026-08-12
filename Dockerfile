FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY pyproject.toml README.md /app/
COPY src /app/src
COPY data /app/data
COPY ui /app/ui

RUN pip install --no-cache-dir -e ".[ui]"

EXPOSE 8000 8501
CMD ["uvicorn", "acreops.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
