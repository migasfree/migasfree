import os
import subprocess
from django.conf import settings


def is_db_postgres():
    return settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql_psycopg2'


def pg_hba_file():
    _cmd = """
    su - postgres -c "psql -t -P format=unaligned -c 'show hba_file';"
    """
    process = subprocess.Popen(_cmd, shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    out, err = process.communicate()
    errcode = process.returncode
    if errcode == 0:
        return out.replace("\n", "")
    else:
        return ""


def pg_hba_file_is_config():
    _cmd = """
    grep migasfree %s > /dev/null
    """ % pg_hba_file()
    return (os.system(_cmd) == 0)


def pg_exists_user(name):
    _cmd = """
    su - postgres -c "psql postgres -tAc \\\"SELECT 1 FROM pg_roles WHERE rolname='%s'\\\" | grep -q 1 "
    """ % name
    return (os.system(_cmd) == 0)


def pg_exists_database(name):
    _cmd = """
    su - postgres -c "psql -l | grep %s &> /dev/null"
    """ % name
    return (os.system(_cmd) == 0)


def pg_change_password(name, password):
    _cmd = """
    su - postgres -c "psql -c \\\"ALTER USER %s WITH PASSWORD '%s';\\\" &> /dev/null"
    """  % (name, password)
    return (os.system(_cmd) == 0)


def pg_create_user(name, password):
    _cmd = """
    su - postgres -c "echo -ne '%(password)s\\n%(password)s\\n' | createuser -S -d -R -E -P %(name)s"
    """ % {"name": name, "password": password}
    return (os.system(_cmd) == 0)


def pg_config(name="migasfree", password="migasfree"):
    if is_db_postgres():
        if not pg_hba_file_is_config():
            _cmd = """
            service postgresql initdb &>/dev/null || :
            _CAD='\# Put your actual configuration here'
            sed -i "s/$_CAD/$_CAD\\nlocal   migasfree             %(user)s                     password\\nlocal   test_migasfree        %(user)s                     password\\n/g" %(file)s
            service postgresql restart
            """ % {"user": name, "file": pg_hba_file()}
            os.system(_cmd)
        if not pg_exists_user(name):
            pg_create_user(name, password)
        if not pg_exists_database("migasfree"):
            os.system("echo y | /usr/bin/migasfree-server-from-scratch")
