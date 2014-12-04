#!/usr/bin/env python

from fabric.api import local, cd, abort, execute
from fabric.contrib.console import confirm


def check_root():
    user = local("whoami", capture = True)
    if not user.contains('root'):
        abort("Must be root to run.")


# Install these:
def prereqs():
    local("apt-get install python-pip git-core python-lxml python-tornado python-beautifulsoup python-dev python-yaml ")
    local("pip install msgpack-python")
    local("apt-get install postgresql python-psycopg2")


# Setup Web2py
def setup_web2py():
    with cd("/opt"):
        local("git clone https://github.com/web2py/web2py.git web2py")


def get_postgres_version():
    pass


# Verify postgres configuration to permit 'md5' login for localhost.
def verify_postgres():
    '''
     Ensure METHOD for IPv4 and IPv6 are set to "md5":
     local   all             all                                     md5
     IPv4 local connections:
     host    all             all             127.0.0.1/32            md5
     IPv6 local connections:
     host    all             all             ::1/128                 md5
    # TODO: Make this check itself.
    '''
    print '''In pg_hba.conf ensure METHOD for IPv4 and IPv6 are set to "md5":
local   all             all                                     md5
IPv4 local connections:
host    all             all             127.0.0.1/32            md5
IPv6 local connections:
host    all             all             ::1/128                 md5'''
    if confirm("Open pg_hba.conf to check?"):
        local("sudo -u postgres vi /etc/postgresql/*/main/pg_hba.conf")
    else:
        print "Not checking file."
        print "Continuing..."


def check_postgres_conf():
    pass


# postgresql will listen on the metasploit port: 5432
# TODO: make this lookup the current posgres config and use that port
def check_posgres_port():
    pass


def create_kvasir_user():
    print "Creating the kvasir db user."
    print "Use a password you can remember."
    local("sudo -u postgres createuser -SleEPRD kvasir")


# Create the Kvasir postgres database
def create_kvasir_db():
    local("sudo -u postgres createdb kvasir -O kvasir")


# Create a self-signed SSL Certificate to be used for web2py and postgres
def create_certs():
    local("openssl genrsa -out server.key 2048")
    local("openssl req -new -key server.key -out server.csr")
    local("openssl x509 -req -days 1095 -in server.csr \
             -signkey server.key -out server.crt")


# OPTIONAL: Verify that postgres can access
# the SSL certificates you expect it will use
# Ubuntu defaults to the snakeoil certs
def verify_ssl():
    local("ls -al /etc/ssl/private/server.key")
    if confirm("Did the permission resemble -rw-r--rw-r----- 1 root ssl-cert ?"):
        local("ls -al /etc/ssl/certs/server.crt")
        if confirm("Did the permissions resemble -rw-r--rw-rw-r--r-- 1 root root ?"):
            local("grep 'postgres' /etc/group")
            confirm("Did the previous return:\nssl-cert:x:105:postgres,alice\
                          postgres:x:126:")
    if not confirm("Continue?"):
        abort("Aborting.")


# OPTIONAL: symlink the server.key and server.crt into postgres's run-time data directory
def make_symlinks():
    data_directory = local("grep 'data_directory' /etc/postgresql/*/main/postgresql.conf", capture = True)
    local("ln -s /etc/ssl/private/server.key /var/lib/postgresql/*/main/server.key")
    local("ln -s /etc/ssl/certs/server.crt /var/lib/postgresql/*/main/server.crt")


# Start web2py
def start_web2py():
    with cd("/opt/web2py"):
        local("python web2py.py -c server.crt -k server.key -p 8443 -i 127.0.0.1 --minthreads=40 -a <recycle>")
        #Browse to https://localhost:8443/admin/ and
        print "Enter your web2py administration password in the web page that follows."
        local("iceweasel https://localhost:8443/admin/ ")


def firewall_warning():
    print "NOTE: If listening to an external interface (-i 0.0.0.0) then ensure iptables \
            is configured correctly and be sure to use a strong password! The /admin/ \
            console is enabled to external interfaces when using SSL."


# Kvasir Code Installation
def get_kvasir():
    '''This procedure will install the latest Kvasir code in /opt/Kvasir using the latest version from Github:'''
    with cd("/opt"):
        local("git clone https://github.com/KvasirSecurity/Kvasir.git Kvasir")


# Install Kvasir to web2py
def install_kvasir():
    '''Via Symbolic Link
    Using sym-links will ensure that your web2py/Kvasir codebase is
    always up-to-date with your main Kvasir codebase.
    '''
    with cd("/opt/web2py/applications"):
        local("ln -s /opt/Kvasir kvasir</pre>")


# Git Clone
def clone_kvasir():
    print "Cloning makes a separate git installation of the Kvasir code allowing for updates / branchs / merging."
    print "Alternatively, you can git clone directly from Github."
    with cd("/opt/web2py/applications"):
        if confirm("Clone separate?"):
            # Clone separate
            local("git clone --depth=1 file:///opt/Kvasir kvasir</pre>")
        else:
            # Clone directly
            local("git clone https://github.com/KvasirSecurity/Kvasir.git kvasir")


# Kvasir Setup
# Kvasir ships intentionally broken. You must configure it first! To do this copy the file 'kvasir.yaml.sample' to 'kvasir.yaml'
def configure_kvasir():
    with cd("/opt/web2py/applications"):
        local("cp kvasir.yaml.sample kvasir.yaml")
    # TODO: Auto configure yaml

    # Configure yaml
    print "The database uri option configures where your database is located and \
            follows a standard URI structure. Web2py supports multiple databases \
            via connection strings. As of now only postgresql, sqlite and mysql have \
            been validated to work with Kvasir. Oracle and MicrosoftSQL should work \
            but have not been tested. The URI is set in db -> kvasir -> uri"

    # Database migrate and fake_migrate
    print 'Web2py maintains table sanity through the migrate settings. If you are \
            a single user or multiple users are using the same web interface this \
            setting can remain "True". If you have multiple users with their own \
            Kvasir/web2py instance working on the same database then only \
            ONE user should set this to "True". All others must use "False".'

    print 'Fake_migrate should be set to "False" unless something goes wrong \
            with your database synchronization files. '

    # security_key
    print "The security_key setting is used to define the encryption method \
            and salt value for passwords and other sensitive data in web2py. \
            You should change this value!"

    # databases subdirectory
    print "Web2py requires the databases directory exist. It doesn't automatically \
            create this. From the main Kvasir application directory:"
    with cd():
        local("mkdir databases")

# Validate the setup!
def validate_setup():
    print "Next we will open your browser to https://localhost:8443/kvasir/"
    print "If you see database errors while trying to access the site at this point, \
            you may need to clean up Kvasir/database/* files that web2py creates"


# Adding Users
def instructions():
    print "No user accounts are created by default. Accounts must be created \
            manually @ https://localhost:8443/kvasir/appadmin/insert/db/auth_user. \
            If viewing Kvasir from localhost a link will be shown on the login screen \
            to add a user."

    print 'NOTE If adding users through the web2py ui the "Registration ID" field \
            is required. It must be unique for each user and can be anything like "1" \
            or "fubar" or "d34db33f"'

    print "Users may also be added from a console: \n\
            $ cd /opt/web2py $ ./web2py.py -R applications/Kvasir/private/user.py \
            -S Kvasir -M -A -u username -p password"

    # Import CPE Data
    print "CPE data is used to accurately identify Operating Systems during scan \
            imports. This data can be downloaded from NIST by Kvasir or supplied by you."


# Task Scheduler Agent
def start_task_scheduler():
    # A Task Scheduler Agent is required to run on your system to perform some
    # of the longer running activities such as XML processing, terminal launching, etc.

    print "A Task Scheduler Agent is required to run on your system to perform some \
            of the longer running activities such as XML processing, terminal launching, etc.\
            \n\nThis can be run as an individual process or both the web server and the \
            scheduler can be started."

    with cd("/opt/web2py"):
        if confirm("Start scheduler individually?"):
            # This can be run as an indiviual process:
            local("python web2py.py -K Kvasir,Kvasir,Kvasir")
        else:
            # Or you can start both the web server and the scheduler:
            local("python web2py.py -c server.crt -k server.key -p 8443 -i 127.0.0.1 --minthreads=40 -a <rec")


# Full install
def install():
    execute(check_root)
    execute(prereqs)
    execute(setup_web2py)
    if confirm("Verify that postgres can access the SSL certificates you expect it will use?\
     - Ubuntu defaults to the snakeoil certs."):
        execute(verify_postgres)
    if confirm("Symlink the server.key and server.crt into postgres's run-time data directory"):
        execute(make_symlinks)
    execute(create_kvasir_user)
    execute(create_kvasir_db)
    execute(create_certs)
    if confirm("Verify postgres can access the ssl certs?"):
        execute(verify_ssl)
    if confirm("Make symlinks?"):
        execute(make_symlinks)
    execute(start_web2py)
    execute(firewall_warning)
    execute(get_kvasir)
    execute(install_kvasir)
    execute(clone_kvasir)
    execute(configure_kvasir)
    execute(validate_setup)
    execute(instructions)
