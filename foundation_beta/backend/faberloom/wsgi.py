"""WSGI config for FaberLoom Foundation Beta."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "faberloom.settings")

application = get_wsgi_application()
