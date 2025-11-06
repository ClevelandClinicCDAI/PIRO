FROM mcr.microsoft.com/mssql-tools
USER root
RUN apt-get update && apt-get install -y curl python3 && rm -rf /var/lib/apt/lists/*
WORKDIR /seed
COPY piro-sql /seed/piro-sql
COPY docker/sample-data/sample-data.sql /seed/sample-data.sql
COPY docker/sample-data/solr-case-docs.json /seed/solr-case-docs.json
COPY docker/sample-data/solr-cohort-docs.json /seed/solr-cohort-docs.json
COPY docker/sample-data/solr-suggest-case.json /seed/solr-suggest-case.json
COPY docker/sample-data/solr-suggest-comment.json /seed/solr-suggest-comment.json
COPY docker/sample-data/solr-suggest-staff.json /seed/solr-suggest-staff.json
COPY docker/sample-data/entrypoint.sh /usr/local/bin/seed.sh
COPY docker/sample-data/table_order.py /usr/local/bin/table-order.py
RUN chmod +x /usr/local/bin/seed.sh /usr/local/bin/table-order.py
ENTRYPOINT ["/usr/local/bin/seed.sh"]
