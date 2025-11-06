## PIRO: A web-based search platform for pathology reports, leveraging large language models to generate discrete searchable insights

[Journal Link](https://www.sciencedirect.com/science/article/pii/S2153353925000215)

This page documents the technologies and applications used to build PIRO, including the web application that provides the user interface, and various back-end ETL and database/full-text search tools.

# Angular Website User Interface
This is an Angular javascript framework application that provides the user interface to PIRO, serving up content in the form of a 'single page application' (SPA).  It retrieves data from the Python/FastAPI REST API.

The files for this application are served up by Nginx on the webserver.  The files are located in the `/opt/piro-ui` directory on the server.

# Python/FastAPI Application
This application is a RESTful API serving up content from the MS SQL Server Database and SOLR to the Angular application.  It's responsibilities include user authentication and authorization checks, data validation (no validation is performed in the Angular Web Interface), creation/retrieval/updating/deleting of user-specific profile information, and it acts as an interface to the Solr instance.  

NGINX is used as a reverse proxy, enforcing HTTPS for all web requests. It proxies to a gunicorn instance, which in turn proxies to the uvicorn workers used by FastAPI.

At launch this application is using LDAP authentication.  But the plan is to, eventually, switch to SSO authentication for a better user experience.

# MS SQL Server Database
The Microsoft SQL Server database is the primary repository of PIRO data.  While most searching occurs against SOLR, the application also utilizes this database for storing/retrieving some PIRO data.  Uses for the data from this database include: user profile information and application configuration information, among other things.  We also stage data in this database before loading it into Solr.

# Solr
PIRO utilizes an Apache Solr instance.  Solr provides the main search feature that is the core of PIRO.

This instance of Solr resides on the PIRO web server.  PIRO data is loaded into Solr on a regular basis - via Airflow - to facilitate the search features in the PIRO interface.

## SSIS
Additionally, we use Microsoft's SSIS software to load data into PIRO from the Clarity database.  The code for these load jobs resides on the database server itself, and is executed from those servers (Note: this is a different server than our primary DB server - one specifically for SSIS).

The SSIS jobs are triggered via our Airflow server (DAG names: 'ssis_delta_load_job' & 'ssis_full_load_job').  The Airflow servers execute a stored procedure to fire off the jobs on the SSIS server.

# Airflow
We use an instance of the Apache Airflow application as a job scheduling tool for PIRO.  It is used primarily to load data: from the Clarity database into PIRO's SQL Server instance, and from PIRO's SQL Server instance into Solr, along with other duties.
