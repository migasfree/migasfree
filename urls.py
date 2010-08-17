from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
from django.contrib import admin
admin.autodiscover()


from migasfree.system.views import *

#from django.contrib.auth.views import login, logout

urlpatterns = patterns('',
    # Example:
#    (r'^migasfree/', include('migasfree.migasfree.urls')),


    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:

    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),



    # Uncomment the next line to enable the admin:
#    (r'^migasfree/admin/', include(admin.site.urls)),


    (r'^migasfree/admin/(.*)', admin.site.root),


    (r'^migasfree/doc/', include('django.contrib.admindocs.urls')),


#    (r'^migasfree/jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),
#    (r'^migasfree/jsi18n', 'django.views.i18n.javascript_catalog'),


    (r'^migasfree/main/(.*)', main),
    (r'^migasfree/system/(.*)', system),
    (r'^migasfree/createrepositories/(.*)', createrepositories),
    (r'^migasfree/directupload/(.*)', directupload),
    (r'^migasfree/update/(.*)', update),
    (r'^migasfree/query/(.*)', query),
    (r'^migasfree/device/(.*)', device),
    (r'^migasfree/info/(.*)', info),
    (r'^migasfree/version/(.*)', changeVersion),
    (r'^migasfree/softwarebase/(.*)', softwarebase),
    (r'^migasfree/uploadPackage/(.*)', uploadPackage),
    (r'^migasfree/uploadSet/(.*)', uploadSet),
    (r'^migasfree/createrepositoriesofpackage/(.*)', createrepositoriesofpackage),
    (r'^migasfree/login/(.*)', login),
    (r'^migasfree/documentation/(.*)', documentation),
)




