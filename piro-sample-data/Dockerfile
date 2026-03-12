FROM mcr.microsoft.com/mssql-tools
USER root
RUN apt-get update && apt-get install -y --no-install-recommends bash curl python3 && rm -rf /var/lib/apt/lists/*
WORKDIR /seed
COPY piro-sql /seed/piro-sql
COPY piro-sample-data/sample-data.sql /seed/sample-data.sql
COPY piro-sample-data/solr-case-docs.json /seed/solr-case-docs.json
COPY piro-sample-data/solr-cohort-docs.json /seed/solr-cohort-docs.json
COPY piro-sample-data/solr-suggest-case.json /seed/solr-suggest-case.json
COPY piro-sample-data/solr-suggest-comment.json /seed/solr-suggest-comment.json
COPY piro-sample-data/solr-suggest-staff.json /seed/solr-suggest-staff.json
COPY piro-sample-data/entrypoint.sh /usr/local/bin/seed.sh
COPY piro-sample-data/table_order.py /usr/local/bin/table-order.py
RUN sed -i 's/\r$//' /usr/local/bin/seed.sh && chmod +x /usr/local/bin/seed.sh /usr/local/bin/table-order.py
ENTRYPOINT ["/bin/bash", "/usr/local/bin/seed.sh"]
