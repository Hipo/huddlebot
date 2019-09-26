FROM python:3.7.1-stretch as base

RUN apt-get update && \
    apt-get dist-upgrade -y && \
    apt-get -y --no-install-recommends install \
    gdal-bin \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -U pip && pip install -r requirements.txt

WORKDIR /huddlebot


## Development
FROM base as application_development
COPY requirements_development.txt .
RUN pip install -U pip && pip install -r requirements_development.txt

# Non Development
FROM base as application
COPY . .
