_DIR_MIGASFREE=/srv/Django/migasfree
_DIR_REPO=/var/www/htdocs/repo


cd $_DIR_MIGASFREE
ln -s $_DIR_MIGASFREE $_DIR_MIGASFREE/utils/db/migasfree 
 
#down documentation
wget --no-cache -O /var/www/htdocs/repo/documentation/es/quick_start.pdf http://migasfree.org/doc/es/quick_start.pdf 

#remove DataBase
rm migasfree.db
#create DataBase
python manage.py syncdb

#permissions for migasfree
chown -R www-data $_DIR_MIGASFREE

mkdir -p /var/www/htdocs/media
chown www-data /var/www/htdocs/media
mkdir -p /var/www/htdocs/repo
chown www-data /var/www/htdocs/repo

rm -r $_DIR_REPO/FEDORA
rm -r $_DIR_REPO/OPENSUSE
rm -r $_DIR_REPO/UBUNTU

#restart apache
/etc/init.d/apache2 restart

#load initial data
export DJANGO_SETTINGS_MODULE=migasfree.settings
python utils/db/initial_data.py

#save fixture for test
python manage.py dumpdata>$_DIR_MIGASFREE/test.json

#run test
python manage.py test


