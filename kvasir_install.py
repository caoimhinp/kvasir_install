#!/usr/bin/env python

import sh
import os
import sys


# Install these:
apt-get install python-pip git-core python-lxml python-tornado python-beautifulsoup python-dev python-yaml
pip install msgpack-python


# Then install these:
apt-get install postgresql python-psycopg2


# Setup Web2py and postgresql
$ cd /opt
$ git clone https://github.com/web2py/web2py.git web2py


# Verify postgres configuration to permit 'md5' login for localhost:

$ sudo -u postgres vi /etc/postgresql/<version>/main/pg_hba.conf

Ensure METHOD for IPv4 and IPv6 are set to "md5":
local   all             all                                     md5
# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
# IPv6 local connections:
host    all             all             ::1/128                 md5


# postgresql will listen on the metasploit port: 5432
# TODO: make this lookup the current posgres config and use that port

# run this command in an interactive shell and give the following instructions:
sudo -u postgres createuser -SleEPRD kvasir

# Instructions:
Enter password for new role:
Enter it again:
CREATE ROLE kvasir PASSWORD 'md5<hash>' NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT LOGIN;

# Create the Kvasir postgres database
sudo -u postgres createdb kvasir -O kvasir

# Create a self-signed SSL Certificate to be used for web2py and postgres
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr
openssl x509 -req -days 1095 -in server.csr -signkey server.key -out server.crt

