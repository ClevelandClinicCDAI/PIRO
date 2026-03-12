FROM solr:9.6
USER root
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY piro-solr/V9 /opt/piro-solr/V9
COPY piro-solr/create-cores.sh /docker-entrypoint-initdb.d/10-create-cores.sh
RUN sed -i 's/\r$//' /docker-entrypoint-initdb.d/10-create-cores.sh
RUN chmod +x /docker-entrypoint-initdb.d/10-create-cores.sh
USER solr
