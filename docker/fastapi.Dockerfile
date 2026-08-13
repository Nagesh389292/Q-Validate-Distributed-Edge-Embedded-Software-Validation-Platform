FROM python:3.13-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn psycopg2-binary opentelemetry-api opentelemetry-sdk prometheus-client pytest kubernetes
COPY python-validation-engine/ /app/
COPY database/ /app/database/
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "qvalidate.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
