"""
WSGI config for library_hackathon project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_hackathon.settings')

application = get_wsgi_application()
