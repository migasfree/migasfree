import os
import psutil

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "migasfree.settings.production")

application = get_wsgi_application()

p = psutil.Process(os.getpid())
p.ionice(psutil.IOPRIO_CLASS_IDLE)
