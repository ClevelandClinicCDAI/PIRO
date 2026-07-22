# PIRO Airflow Servers

This file provides example documentation of the Airflow installation process for `piro-airflow` on a Linux server.

## Important Directories & Files

* Airflow config file: /home/piro-builder/airflow/airflow.cfg
* SSL Certificates: /etc/ssl/certs/
* Codebase: /opt/piro-airflow/piro-airflow

## Useful Commands

* Airflow Services
  * Service management script directory: `/home/piro-builder/airflow/systemd_service_management_scripts`
    * Start all Airflow services: `sudo bash start_services.sh`
    * Stop all Airflow services: `sudo bash stop_services.sh`
    * Check status for all Airflow services: `sudo bash status_services.sh`
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
    * `sudo apt-get install build-essential pkg-config python3-dev python3.12 python3.12-dev python3.12-venv`
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
    * `python3.12 -m venv piro-airflow_venv`
    * `source /opt/piro-airflow/piro-airflow_venv/bin/activate`
1. Initial Deployment
    * Review the scripts `azure-pipelines-dev.yml` and `azure-pipelines.yml` and note the directory used in the `rsync` step of the script.  Create the directory if needed.
    * Execute the appropriate pipeline within our codebase to deploy the code to the server.  This should copy the code itself into the target directory (via `rsync`) and should also install python packages into the venv.
    * Confirm that the code was copied to the server properly and that the venv has the necessary packages installed.
1. Set up SystemD services for Airflow:
    * Create the following files
    * /etc/systemd/system/piro-airflow-dag-processor.service:

        ```bash
            #piro-airflow-dag-processor.service

            [Unit]
            Description=PIRO Airflow dag-processor daemon
            After=network.target postgresql.service
            Wants=postgresql.service

            [Service]
            Environment="PATH=/opt/piro-airflow/piro-airflow_venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
            User=piro-builder
            Group=piro-builder
            Type=simple
            ExecStart=/opt/piro-airflow/piro-airflow_venv/bin/airflow dag-processor
            Restart=always
            RestartSec=5s

            [Install]
            WantedBy=multi-user.target
        ```

    * /etc/systemd/system/piro-airflow-triggerer.service:

        ```bash
            #piro-airflow-triggerer.service

            [Unit]
            Description=PIRO Airflow triggerer daemon
            After=network.target postgresql.service piro-airflow-dag-processor.service
            Wants=postgresql.service piro-airflow-dag-processor.service

            [Service]
            Environment="PATH=/opt/piro-airflow/piro-airflow_venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
            User=piro-builder
            Group=piro-builder
            Type=simple
            ExecStart=/opt/piro-airflow/piro-airflow_venv/bin/airflow triggerer
            Restart=always
            RestartSec=5s

            [Install]
            WantedBy=multi-user.target
        ```

    * /etc/systemd/system/piro-airflow-scheduler.service:

        ```bash
            #piro-airflow-scheduler.service

            [Unit]
            Description=PIRO Airflow scheduler daemon
            After=network.target postgresql.service piro-airflow-triggerer.service
            Wants=postgresql.service piro-airflow-triggerer.service

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
            After=network.target postgresql.service piro-airflow-scheduler.service
            Wants=postgresql.service piro-airflow-scheduler.service

            [Service]
            Environment="PATH=/opt/piro-airflow/piro-airflow_venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
            User=piro-builder
            Group=piro-builder
            Type=simple
            ExecStart=/opt/piro-airflow/piro-airflow_venv/bin/airflow api-server -p 8080 --proxy-headers
            Restart=on-failure
            RestartSec=5s
            PrivateTmp=true

            [Install]
            WantedBy=multi-user.target
        ```

    * Enable the services (one-time setup):
        * Ensure these service units are enabled so they start on boot:
            * `piro-airflow-dag-processor`
            * `piro-airflow-triggerer`
            * `piro-airflow-scheduler`
            * `piro-airflow-webserver`

    * Service management scripts:
        * Location on server: `/home/piro-builder/airflow/systemd_service_management_scripts`
        * These scripts can be used to start, stop, and check all PIRO Airflow services together.

        * `start_services.sh`

            ```bash
            #!/bin/bash
            # Start all PIRO Airflow systemd services

            SERVICES=(
                "piro-airflow-dag-processor"
                "piro-airflow-triggerer"
                "piro-airflow-scheduler"
                "piro-airflow-webserver"
            )

            echo "Starting PIRO Airflow services..."
            echo "-----------------------------------"

            for service in "${SERVICES[@]}"; do
                echo -n "Starting ${service}... "
                sudo systemctl start "${service}"
                if [ $? -eq 0 ]; then
                    echo "OK"
                else
                    echo "FAILED"
                fi
            done

            echo "-----------------------------------"
            echo "Done. Run status_services.sh to verify."
            ```

        * `stop_services.sh`

            ```bash
            #!/bin/bash
            # Stop all PIRO Airflow systemd services

            SERVICES=(
                "piro-airflow-webserver"
                "piro-airflow-scheduler"
                "piro-airflow-triggerer"
                "piro-airflow-dag-processor"
            )

            echo "Stopping PIRO Airflow services..."
            echo "-----------------------------------"

            for service in "${SERVICES[@]}"; do
                echo -n "Stopping ${service}... "
                sudo systemctl stop "${service}"
                if [ $? -eq 0 ]; then
                    echo "OK"
                else
                    echo "FAILED"
                fi
            done

            echo "-----------------------------------"
            echo "Done. Run status_services.sh to verify."
            ```

        * `status_services.sh`

            ```bash
            #!/bin/bash
            # Check status of all PIRO Airflow systemd services

            SERVICES=(
                "piro-airflow-dag-processor"
                "piro-airflow-triggerer"
                "piro-airflow-scheduler"
                "piro-airflow-webserver"
            )

            echo "PIRO Airflow Service Status"
            echo "============================="

            for service in "${SERVICES[@]}"; do
                echo ""
                echo "[ ${service} ]"
                sudo systemctl status "${service}" --no-pager -l
                echo "------------------------------"
            done
            ```

1. Install and Enable Postgres:
    * Note: we prefer PostgreSQL v16, if possible, and this may require additional apt repos to be added.  Adjust the commands below as necessary.
    * `sudo apt install postgresql postgresql-contrib`
    * `systemctl start postgresql.service`
1. Set up the Airflow Postgres database:
    * Create a password for 'airflow_user' in Secret Server/Thycotic.
    * `sudo -u postgres psql` to access the command prompt.
    * `CREATE DATABASE airflow_db;`
    * `CREATE USER airflow_user WITH PASSWORD '<airflow_user password>';`
    * `ALTER DATABASE airflow_db OWNER TO airflow_user;`
1. Create a 'Fernet Key' to encrypt Airflow Secrets:
    * With the project venv activated:
        * `python`
        * `from cryptography.fernet import Fernet`
        * `fernet_key = Fernet.generate_key()`
        * `print(fernet_key.decode())`
    * Capture the printed secret in Thycotic
1. Edit the Airflow config file, `/home/piro-builder/airflow/airflow.cfg`:
    * Be sure to add the values to the file in the appropriate sections, as listed below (this list is not comprehensive, and only contains those settings that are either vital or need to be changed from the defaults).:
    * `[core]`
      * `dags_folder` = /opt/piro-airflow/piro-airflow
      * `executor` = LocalExecutor
      * `auth_manager` = airflow.providers.fab.auth_manager.fab_auth_manager.FabAuthManager
      * `load_examples` = False
      * `fernet_key` = `<Airflow "fernet" password>`
      * `allowed_deserialization_classes` = airflow.*
      * `sensitive_var_conn_names` = key,path,keys,encrypt,encrypted
    * `[database]`
      * `sql_alchemy_conn` = postgresql+psycopg2://airflow_user:`<airflow postgres database password>`@localhost:5432/airflow_db
    * `[api]`
      * `host` = 0.0.0.0
      * `port` = 8080
      * `secret_key` = `<a thoroughly random value>` # does not need to be added to Secret Server
    * `[api_auth]`
      * `jwt_secret` = `<Airflow "jwt" secret>`
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
1. Turn on Airflow Services
    * `cd /home/piro-builder/airflow/systemd_service_management_scripts`
    * `sudo bash start_services.sh`
    * `sudo bash status_services.sh`
