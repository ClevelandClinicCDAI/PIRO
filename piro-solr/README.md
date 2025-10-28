# Introduction

SOLR SETUP on the Application Servers.

## JAVA

INSTALL JAVA
sudo apt-get install openjdk-17-jdk

UPDATE JAVA
sudo update-alternatives --config java

From <https://superuser.com/questions/569633/what-is-command-to-see-all-java-versions-installed-on-linux>

sudo update-alternatives --config javac

## SOLR Setup

Download SOLR
cd /opt/search/software/solr-9.8.1
sudo wget <https://dlcdn.apache.org/solr/solr/9.8.1/solr-9.8.1.tgz>
sudo tar xzf solr-9.8.1.tgz

Install SOLR
cd /opt/solr
cp -r /opt/search/software/solr-9.8.1 .
chmod 777 -R solr-9.8.1/

## SOLR Start

STOP Solr
./solr stop -p 8983

START Solr
./solr start -Denable.packages=true

## Create Collection

COPY The config folders from the git repo to a directory on the server.

cd /opt/solr/solr-9.8.1/bin
cp -R [source code folder]/solr/V9/* /opt/solr/config/V9/ [Copy the config schema folders]

cp -R /opt/solr/config/V9/PIROCase/ /opt/solr/solr-9.8.1/server/solr/
./solr create_core -c PIROCase -s <http://localhost:8983> -d /opt/solr/solr-9.8.1/server/solr/PIROCase/

cp -R /opt/solr/config/V9/PIROCohort/ /opt/solr/solr-9.8.1/server/solr/
./solr create_core -c PIROCohort -s <http://localhost:8983> -d /opt/solr/solr-9.8.1/server/solr/PIROCohort/

cp -R /opt/solr/config/V9/PIROSuggestCase/ /opt/solr/solr-9.8.1/server/solr/
./solr create_core -c PIROSuggestCase -s <http://localhost:8983> -d /opt/solr/solr-9.8.1/server/solr/PIROSuggestCase/

cp -R /opt/solr/config/V9/PIROSuggestStaff/ /opt/solr/solr-9.8.1/server/solr/
./solr create_core -c PIROSuggestStaff -s <http://localhost:8983> -d /opt/solr/solr-9.8.1/server/solr/PIROSuggestStaff/

## Delete Collection

cd /opt/solr/solr-9.8.1/bin
./solr delete -c PIROCase
./solr delete -c PIROCohort
./solr delete -c PIROSuggestCase
./solr delete -c PIROSuggestStaff

## Authentication and Security

SET Authentication and Admin Password
Add the below in solr.in.sh file
SOLR_AUTH_TYPE="basic"
SOLR_AUTHENTICATION_OPTS="-Dbasicauth=solr-piro-adm:XXXXXXX"

cd /opt/solr/solr-9.8.1/bin
vi solr.in.sh

Copy the security.json file
cp /opt/solr/solr-8.11.2/server/solr/security.json /opt/solr/solr-9.8.1/server/solr/

curl --user solr:[password] <http://localhost:8983/api/cluster/security/authentication> -H 'Content-type:application/json' -d '{"set-user": {"tom":"Password", "harry":"Password"}}' -H 'Authorization: Basic solr-piro-adm:XXXXXXXXXXXXX'

Authentication Note: solr commands will fail authentication. Disable the authentication by renaming the security.json file in the folder /opt/solr/solr-9.8.1/server/solr and restarting the SOLR Server. Run the solr commands and then rename the file back to security.json and restart the server to enable the authentication

## Ngnix Config - SSL Certs (Proxy Redirection)

cd /etc/nginx/sites-available
sudo vi solr-8989

server {
    server_name [hostname];

    listen 8989 ssl;

    ssl_certificate /etc/ssl/certs/[hostname].cer;
    ssl_certificate_key /etc/ssl/certs/[hostname].key;

    ssl_session_cache  builtin:1000  shared:SSL:10m;
    ssl_protocols  TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!eNULL:!EXPORT:!CAMELLIA:!DES:!MD5:!PSK:!RC4;
    ssl_prefer_server_ciphers on;
   client_max_body_size 96M;
    location / {
        include proxy_params;
        proxy_pass <http://127.0.0.1:8983>;
    }
}

sudo vi solr-8990

server {
    server_name [hostname];

    listen 8990 ssl;

    ssl_certificate /etc/ssl/certs/[hostname].cer;
    ssl_certificate_key /etc/ssl/certs/[hostname].key;

    ssl_session_cache  builtin:1000  shared:SSL:10m;
    ssl_protocols  TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!eNULL:!EXPORT:!CAMELLIA:!DES:!MD5:!PSK:!RC4;
    ssl_prefer_server_ciphers on;

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8984;
    }
}

sudo ln -s /etc/nginx/sites-available/solr-8989 /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/solr-8990 /etc/nginx/sites-enabled/

## Ngnix - Restart

/etc/init.d/nginx stop
/etc/init.d/nginx start

## SOLR Service - Update

cd /etc/systemd/system
sudo vi solr.service

[Unit]
Description=Apache SOLR
ConditionPathExists=/opt/solr
After=syslog.target network.target remote-fs.target nss-lookup.target systemd-journald-dev-log.socket
Before=multi-user.target

[Service]
User=piro-user
Group=piro-user
Type=forking
PIDFile=/opt/solr/solr-9.8.1/bin/solr-8983.pid
Environment=SOLR_INCLUDE=/opt/solr/solr-9.8.1/bin/solr.in.sh
Restart=on-failure
ExecStart=/opt/solr/solr-9.8.1/bin/solr start -q -Denable.dih.dataConfigParam=true
ExecStop=/opt/solr/solr-9.8.1/bin/solr stop

[Install]
WantedBy=multi-user.target

## SOLR Service - Restart

sudo systemctl daemon-reload
sudo systemctl stop solr
sudo systemctl start solr
