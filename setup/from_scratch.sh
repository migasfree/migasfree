#!/bin/bash

. $(cd $(dirname $0); pwd -P)/web_server.sh
. $(cd $(dirname $0); pwd -P)/db_server.sh

# main process

read -e -p "Have you checked migasfree.settings before start from scratch? This procedure remove existing data in app. [y/n] " _RESPONSE

if [ -z "$_RESPONSE" -o "$_RESPONSE" != 'y' ]
then
    echo "Aborted process. Review migasfree.settings and try again."
    exit 1
fi

remove_database
db_server_init
web_server_init

echo
echo "migasfree server operative. Test it at http://localhost/"
echo

exit 0
