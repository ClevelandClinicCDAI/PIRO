FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl apt-transport-https gnupg unixodbc-dev build-essential && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    echo "deb [arch=amd64] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /tmp/requirements.txt
COPY core_requirements.txt /tmp/core_requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY backend /app
ENV PYTHONPATH=/app
EXPOSE 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
