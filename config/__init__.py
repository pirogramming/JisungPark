from __future__ import absolute_import, unicode_literals
from .celery_app import app as celery_app  # Celery 앱 호출

__all__ = ('celery_app',)