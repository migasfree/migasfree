#!/bin/bash

#http://www.logilab.org/card/pylintfeatures
#http://gramps-project.org/wiki/index.php?title=Programming_guidelines

#must be installed pylint : apt-get install pylint

export DJANGO_SETTINGS_MODULE=migasfree.settings

function check
{
    pylint --rcfile=$_DIRNAME/check-migasfree.rc -i y -r n $1 > check.txt
    if [ $? -ne 0 ]
    then
        less check.txt
    fi
}

# main
_DIRNAME=$PWD
cd ../..
export -f check
find . -name "*.py" -exec bash -c 'check {}' \;
