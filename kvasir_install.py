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

OPTIONAL: Verify that postgres can access the SSL certificates you expect it will use - Ubuntu defaults to the snakeoil certs

$ ls -al /etc/ssl/private/server.key
-rw-r----- 1 root ssl-cert ...
$ ls -al /etc/ssl/certs/server.crt
-rw-r--r-- 1 root root ...
$ grep 'postgres' /etc/group
ssl-cert:x:105:postgres,alice
postgres:x:126:
OPTIONAL: symlink the server.key and server.crt into postgres's run-time data directory

$ grep 'data_directory' /etc/postgresql/<version>/main/postgresql.conf
data_directory = '/var/lib/postgresql/<version>/main'

$ ln -s /etc/ssl/private/server.key /var/lib/postgresql/<version>/main/server.key
$ ln -s /etc/ssl/certs/server.crt /var/lib/postgresql/<version>/main/server.crt
Start web2py

cd /opt/web2py
python web2py.py -c server.crt -k server.key -p 8443 -i 127.0.0.1 --minthreads=40 -a <recycle>
Browse to https://localhost:8443/admin/ and enter your web2py administration password.

NOTE: If listening to an external interface (-i 0.0.0.0) then ensure iptables is configured correctly and be sure to use a strong password! The /admin/ console is enabled to external interfaces when using SSL.

Kvasir Code Installation

This procedure will install the latest Kvasir code in /opt/Kvasir using the latest version from Github:

$ cd /opt
$ git clone https://github.com/KvasirSecurity/Kvasir.git Kvasir
Install Kvasir to web2py

Kvasir's design is lightweight allowing installation as unique applications in web2py.

Via Symbolic Link

Using sym-links will ensure that your web2py/Kvasir codebase is always up-to-date with your main Kvasir codebase.

$ cd /opt/web2py/applications
$ ln -s /opt/Kvasir kvasir</pre>
Git Clone

Cloning makes a separate git installation of the Kvasir code allowing for updates / branchs / merging.

$ cd /opt/web2py/applications
$ git clone --depth=1 file:///opt/Kvasir kvasir</pre>
Alternatively you can git clone directly from Github:

$ cd /opt/web2py/applications
$ git clone https://github.com/KvasirSecurity/Kvasir.git kvasir
Kvasir Setup

Kvasir ships intentionally broken. You must configure it first! To do this copy the file 'kvasir.yaml.sample' to 'kvasir.yaml'

Kvasir database uri

The database uri option configures where your database is located and follows a standard URI structure. Web2py supports multiple databases via connection strings. As of now only postgresql, sqlite and mysql have been validated to work with Kvasir. Oracle and MicrosoftSQL should work but have not been tested.

The URI is set in db -> kvasir -> uri

Database migrate and fake_migrate

Web2py maintains table sanity through the migrate settings. If you are a single user or multiple users are using the same web interface this setting can remain "True". If you have multiple users with their own Kvasir/web2py instance working on the same database then only ONE user should set this to "True". All others must use "False".

Fake_migrate should be set to "False" unless something goes wrong with your database synchronization files.

security_key

The security_key setting is used to define the encryption method and salt value for passwords and other sensitive data in web2py. You should change this value!

databases subdirectory

Web2py requires the databases directory exist. It doesn't automatically create this. From the main Kvasir application directory:

$ mkdir databases
Validate the setup!

Open your browser to https://localhost:8443/kvasir/
If you see database errors while trying to access the site at this point, you may need to clean up Kvasir/database/* files that web2py creates
Adding Users

No user accounts are created by default. Accounts must be created manually @ https://localhost:8443/kvasir/appadmin/insert/db/auth_user. If viewing Kvasir from localhost a link will be shown on the login screen to add a user.

NOTE If adding users through the web2py ui the "Registration ID" field is required. It must be unique for each user and can be anything like "1" or "fubar" or "d34db33f"

Users may also be added from a console:

$ cd /opt/web2py $ ./web2py.py -R applications/Kvasir/private/user.py -S Kvasir -M -A -u username -p password

Import CPE Data

CPE data is used to accurately identify Operating Systems during scan imports. This data can be downloaded from NIST by Kvasir or supplied by you.

Task Scheduler Agent

A Task Scheduler Agent is required to run on your system to perform some of the longer running activities such as XML processing, terminal launching, etc. This can be run as an indiviual process:

$ cd /opt/web2py
$ python web2py.py -K Kvasir,Kvasir,Kvasir
Or you can start both the web server and the scheduler:

$ cd /opt/web2py
$ python web2py.py -c server.crt -k server.key -p 8443 -i 127.0.0.1 --minthreads=40 -a <rec
