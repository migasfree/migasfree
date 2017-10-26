#!/bin/bash

function version_gt()
{
    test "$(echo "$@" | tr " " "\n" | sort -V | head -n 1)" != "$1";
}

function get_migasfree_setting()
{
    echo -n $(DJANGO_SETTINGS_MODULE=migasfree.settings.production python -c "from django.conf import settings; print settings.$1")
}

# owner resource user
function owner()
{
    if [ ! -f "$1" -a ! -d "$1" ]
    then
        mkdir -p "$1"
    fi

    _OWNER=$(stat -c %U "$1" 2>/dev/null)
    if [ "$_OWNER" != "$2" ]
    then
        chown -R $2:$2 "$1"
    fi
}

# service_action service action
function service_action()
{
    _SERVICE=$1
    _ACTION=$2

    /etc/init.d/"$_SERVICE" "$_ACTION"
}

# boot_at_start service
function boot_at_start()
{
    _SERVICE=$1

    if which update-rc.d &> /dev/null
    then
        update-rc.d "$_SERVICE" defaults || :
    elif which chkconfig &> /dev/null
    then
        chkconfig --add "$_SERVICE" || :
    fi
}
