from .celery import celery_app

# Initialize Celery App upon Django Start
__all__ = ('celery_app', )