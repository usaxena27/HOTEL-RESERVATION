FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -e .

# Comment this out for now - run training after container starts or separately
# RUN python pipeline/training_pipeline.py

EXPOSE 5000

CMD ["python", "application.py"]