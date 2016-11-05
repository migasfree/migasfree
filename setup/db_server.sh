#!/bin/bash

. ${BASH_SOURCE%/*}/common.sh

function is_postgres_db()
{
    test $(get_migasfree_setting "DATABASES['default']['ENGINE']") == "django.db.backends.postgresql_psycopg2"
}

function is_sqlite_db()
{
    test $(get_migasfree_setting "DATABASES['default']['ENGINE']") == "django.db.backends.sqlite3"
}

function remove_database()
{
    _NAME=$(get_migasfree_setting "DATABASES['default']['NAME']")
    if [ is_sqlite_db -eq 0 ]
    then
        rm -f $_NAME
    else
        su - postgres -c "psql -c 'DROP DATABASE IF EXISTS $_NAME' &>/dev/null"
    fi
}


function get_pg_hba()
{
    echo -n $(su - postgres -c "psql -t -P format=unaligned -c 'show hba_file';")
}

function is_pg_hba_configured()
{
    _NAME=$(get_migasfree_setting "DATABASES['default']['NAME']")
    _FILE=$(get_pg_hba)
    grep -q $_NAME $_FILE
    test $? -eq 0
}

function is_pg_user_exists()
{
    _USER=$(get_migasfree_setting "DATABASES['default']['USER']")
    _CMD="psql postgres -tAc \"SELECT 1 FROM pg_roles WHERE rolname='$_USER';\""
    su postgres -l -c "$_CMD" | grep -q 1
    test $? -eq 0
}

function is_pg_db_exists()
{
    _NAME=$(get_migasfree_setting "DATABASES['default']['NAME']")
    _CMD="psql -tAc \"SELECT 1 FROM pg_database WHERE datname='$_NAME'\""
    su postgres -l -c "$_CMD" | grep -q 1
    test $? -eq 0
}

function pg_create_database()
{
    _NAME=$(get_migasfree_setting "DATABASES['default']['NAME']")
    _USER=$(get_migasfree_setting "DATABASES['default']['USER']")
    _PWD=$(get_migasfree_setting "DATABASES['default']['PASSWORD']")
    _CMD="PGPASSWORD=$_PWD createdb -w -E utf8 -O $_USER $_NAME"
    su postgres -l -c "$_CMD"
    test $? -eq 0
}

function pg_change_pwd()
{
    _USER=$(get_migasfree_setting "DATABASES['default']['USER']")
    _PWD=$(get_migasfree_setting "DATABASES['default']['PASSWORD']")
    _CMD="psql -c \"ALTER USER $_USER WITH PASSWORD '$_PWD';\" &> /dev/null"
    su postgres -l -c "$_CMD"
    test $? -eq 0
}

function pg_create_user()
{
    _USER=$(get_migasfree_setting "DATABASES['default']['USER']")
    _PWD=$(get_migasfree_setting "DATABASES['default']['PASSWORD']")
    _CMD="psql postgres -tAc \"CREATE USER $_USER WITH CREATEDB ENCRYPTED PASSWORD '$_PWD';\""
    su postgres -l -c "$_CMD"
    test $? -eq 0
}

function get_pg_major_version()
{
    echo -n $(psql --version | head -1 | cut -d ' ' -f 3 | cut -d '.' -f1,2)
}

function set_pg_config()
{
    _NAME=$(get_migasfree_setting "DATABASES['default']['NAME']")
    _USER=$(get_migasfree_setting "DATABASES['default']['USER']")
    _CAD="# Put your actual configuration here"
    sed -i "s/$_CAD/$_CAD\\nlocal   $_NAME             $_USER                     password\\n/g" $(get_pg_hba)
}

function db_server_init()
{
    export DJANGO_SETTINGS_MODULE=migasfree.settings.production

    boot_at_start postgresql
    service_action postgresql start
    is_pg_user_exists || pg_create_user

    is_pg_hba_configured || (
        set_pg_config
        service postgresql restart || :
    )

    is_pg_db_exists && echo yes | cat - | django-admin migrate --fake-initial || (
        pg_create_database
        django-admin migrate

        python - << EOF
import django
django.setup()
from migasfree.server.fixtures import (
    create_registers,
    sequence_reset,
)
create_registers()
sequence_reset()
EOF
    )
}
