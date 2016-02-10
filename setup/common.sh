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
