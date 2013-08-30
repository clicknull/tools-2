# Celery configuration file

""" For default worker: celery worker --purge -Q default -A logcrawler.tasks -P eventlet -c 500 -n default-worker
    For analyze worker: celery worker --purge -A logcrawler.tasks -Q analyze -n analyze-worker
""" 

from kombu import Exchange, Queue
from logcrawler.conf.config import CELERY_BROKER, CELERY_BACKEND


BROKER_URL = CELERY_BROKER
CELERY_RESULT_BACKEND = CELERY_BACKEND


CELERY_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('analyze', Exchange('analyze'), routing_key='analyze'),
)
CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_EXCHANGE_TYPE = 'direct'
CELERY_DEFAULT_ROUTING_KEY = 'default'

CELERY_ROUTES = {
    'logcrawler.tasks.analyze_process': {
        'queue': 'analyze',
        'routing_key': 'analyze',
    },
}
