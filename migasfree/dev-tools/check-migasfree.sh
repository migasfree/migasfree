
#http://www.logilab.org/card/pylintfeatures
#http://gramps-project.org/wiki/index.php?title=Programming_guidelines

#must be installed pylint : apt-get install pylint


export DJANGO_SETTINGS_MODULE=migasfree.settings 

function check 
{
  _FILE=$1
  pylint --rcfile=$_DIRNAME/check-migasfree.rc -i y -r n $1 > check.txt
  if ! [ $? = 0 ]; then
    less check.txt
  fi
}


_DIRNAME=$PWD
cd ../..

check "migasfree/settings.py
  migasfree/urls.py
  migasfree/system/admin.py
  migasfree/system/client.py
  migasfree/system/errmfs.py
  migasfree/system/forms.py
  migasfree/system/functions.py
  migasfree/system/hardware.py 
  migasfree/system/logic.py
  migasfree/system/models.py
  migasfree/system/security.py
  migasfree/system/tests.py
  migasfree/system/views.py
  $(which migasfree-server-load-initial-data.py)
"
