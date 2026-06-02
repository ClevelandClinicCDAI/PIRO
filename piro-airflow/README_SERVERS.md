This file provides example documentation of the Airflow installation process for `piro-airflow` on a Linux server.

# Important Directories & Files

* Airflow config file: /home/piro-builder/airflow/airflow.cfg
* SSL Certificates: /etc/ssl/certs/
* Codebase: /opt/piro-airflow/piro-airflow

## Useful Commands

* Airflow Services
  * Checking service status:
    * `sudo systemctl status piro-airflow-scheduler`
    * `sudo systemctl status piro-airflow-webserver`
  * Starting services:
    * `sudo systemctl start piro-airflow-scheduler`
    * `sudo systemctl start piro-airflow-webserver`
  * Stopping services:
    * `sudo systemctl stop piro-airflow-scheduler`
    * `sudo systemctl stop piro-airflow-webserver`
* NGINX
  * Test config changes
    * `sudo nginx -t`
  * Checking service status:
    * `sudo systemctl status nginx`
  * Starting services:
    * `sudo systemctl start nginx`
  * Stopping services:
    * `sudo systemctl stop nginx`

## Server Install Documentation for the PIRO Airflow Servers

1. Install the MS ODBC for Linux
    * See installation instructions here: <https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver15#ubuntu17>
    * You can ignore the optional commands at the end of the instructions
    * MSODBC18 version has been installed in PROD
1. Install system packages
    * `sudo add-apt-repository ppa:deadsnakes/ppa -y`
    * `sudo apt-get install build-essential pkg-config python3-dev python3.11 python3.11-dev python3.11-venv`
1. Create a password for `piro-builder` in Thycotic.
1. Create the `piro-builder` user:
    * `sudo adduser piro-builder`
    * `sudo gpasswd -a piro-builder sudo`
    * Switch to the new user: `su - piro-builder`
1. Set up a folder and deploy the codebase:
    * `cd /opt`
    * `sudo mkdir piro-airflow`
    * `sudo chown piro-builder piro-airflow`
    * `sudo chgrp piro-builder piro-airflow`
    * `cd piro-airflow`
1. Create the venv:
    * `python3.11 -m venv piro-airflow_venv`
    * `source /opt/piro-airflow/piro-airflow_venv/bin/activate`
1. Set up the codebase:
    * `mkdir piro-airflow`
    * `cd piro-airflow`
    * `git clone [piro-airflow git repo url] .`
1. Manually install Airflow
    * `AIRFLOW_VERSION=2.8.0`
    * `PYTHON_VERSION=3.11`
    * `CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"`
    * `pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"`
1. Set up SystemD services for Airflow:
    * Create the following files
    * /etc/systemd/system/piro-airflow-scheduler.service:

        ```bash
        #piro-airflow-scheduler.service

        [Unit]
        Description=PIRO Airflow scheduler daemon
        After=network.target postgresql.service
        Wants=postgresql.service

        [Service]
        Environment="PATH=/opt/piro-airflow/piro-airflow_venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
        User=piro-builder
        Group=piro-builder
        Type=simple
        ExecStart=/opt/piro-airflow/piro-airflow_venv/bin/airflow scheduler
        Restart=always
        RestartSec=5s

        [Install]
        WantedBy=multi-user.target
        ```

    * /etc/systemd/system/piro-airflow-webserver.service:

        ```bash
        #piro-airflow-webserver.service

        [Unit]
        Description=PIRO Airflow webserver daemon
        After=network.target postgresql.service
        Wants=postgresql.service

        [Service]
        Environment="PATH=/opt/piro-airflow/piro-airflow_venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
        User=piro-builder
        Group=piro-builder
        Type=simple
        ExecStart=/opt/piro-airflow/piro-airflow_venv/bin/airflow webserver -p 8080
        Restart=on-failure
        RestartSec=5s
        PrivateTmp=true

        [Install]
        WantedBy=multi-user.target
        ```

    * Start and stop the 'schedule' service to create the 'airflow' folder in the 'piro-builder' account's home folder.

        ```bash
        sudo systemctl start piro-airflow-scheduler
        sudo systemctl stop piro-airflow-scheduler
        ```

1. Install and Enable Postgres:
    * `sudo apt install postgresql postgresql-contrib`
    * `systemctl start postgresql.service`
1. Set up the Airflow Postgres database:
    * Create a password for 'airflow_user' in Secret Server/Thycotic.
    * `sudo -u postgres psql` to access the command prompt.
    * `CREATE DATABASE airflow_db;`
    * `CREATE USER airflow_user WITH PASSWORD '<airflow_user password>';`
    * `GRANT ALL PRIVILEGES ON DATABASE airflow_db TO airflow_user;`
1. Create a 'Fernet Key' to encrypt Airflow Secrets:
    * With the project venv activated:
        * `python`
        * `from cryptography.fernet import Fernet`
        * `fernet_key = Fernet.generate_key()`
        * `print(fernet_key.decode())`
    * Capture the printed secret in Thycotic
1. Edit the Airflow config file, `/home/piro-builder/airflow/airflow.cfg`:
    * dags_folder = /opt/piro-airflow/piro-airflow
    * executor = LocalExecutor
    * load_examples = False
    * sql_alchemy_conn = postgresql+psycopg2://airflow_user:<"airflow postgres database password">@localhost:5432/airflow_db
    * fernet_key = <Airflow "fernet" password>
    * smtp_mail_from = piro-builder@[hostname]
    * auth_backends = airflow.api.auth.backend.basic_auth,airflow.api.auth.backend.session
1. Create the `smtp_default` connection (required in Airflow 3 for failure emails):
    * With the project venv activated:
        * `airflow connections delete smtp_default || true`
        * `airflow connections add smtp_default --conn-json '{"conn_type":"smtp","host":"localhost","port":25,"extra":{"from_email":"piro-builder@build-piro.ccf.org","disable_ssl":true,"disable_tls":false}}'`
        * `airflow connections get smtp_default`
    * Configuration notes:
        * This setup uses localhost SMTP relay (port 25) with STARTTLS enabled (`disable_tls=false`).
        * The `from_email` in the `smtp_default` connection is a fallback; the primary source is the `[email]` section of `airflow.cfg`.
        * For plaintext relay (no TLS), use `disable_tls=true` and `disable_ssl=true`.
        * If you see `[SSL: WRONG_VERSION_NUMBER]`, ensure `disable_ssl=true` (implicit SSL should not be used on port 25).
        * For SMTPS (implicit SSL on port 465), use `disable_ssl=false` and `disable_tls=true`.
1. Pip install psycopg2:
    * With the project venv activated:
        * `pip install psycopg2-binary`
1. Initialize the Airflow DB & set up the Admin user:
    * Create a username/password pair and store in Thycotic.
        * username: 'admin'
    * With the project venv activated:
        * `airflow db init`
        * `airflow users  create --role Admin --username admin --email admin --firstname admin --lastname admin --password '<airflow admin password>'`
1. Copy the TLS certs to /etc/ssl/certs if needed.
1. NGINX config
    * Create a file, '/etc/nginx/sites-available/piro-build', containing the following (adjusting SSL cert filenames if necessary):

        ```nginx
        server {
                listen 443 ssl;

                ssl_certificate /etc/ssl/certs/[cert_file];
                ssl_certificate_key /etc/ssl/certs/[key_file];

                ssl_session_cache  builtin:1000  shared:SSL:10m;
                ssl_protocols  TLSv1.3;
                ssl_ciphers HIGH:!aNULL:!eNULL:!EXPORT:!CAMELLIA:!DES:!MD5:!PSK:!RC4;
                ssl_prefer_server_ciphers on;

                location / {
                        proxy_set_header        Host $host;
                        proxy_set_header        X-Real-IP $remote_addr;
                        proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
                        proxy_set_header        X-Forwarded-Proto $scheme;

                        proxy_pass http://localhost:8080;
                }
        }
        ```

    * Enable the new config file
        * `cd /etc/nginx/sites-enabled/`
        * `sudo ln -s /etc/nginx/sites-available/build-piro build-piro`
        * Also disable the 'default' if needed
        * Test the new config: `nginx -t`
        * Reload the nginx config to activate: `systemctl reload nginx`
1. Install remaining python packages
    * With venv activated, as 'piro-builder' account:
        * `cd /opt/piro-airflow/piro-airflow`
        * `pip install -r requirements.txt`
1. Turn on Airflow Services
    * `sudo systemctl start piro-airflow-scheduler`
    * `sudo systemctl start piro-airflow-webserver`
