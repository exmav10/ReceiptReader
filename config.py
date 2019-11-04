import os

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

API_CONNECTION = {
    'host': os.environ.get('API_HOST', '0.0.0.0'),
    'port': int(os.environ.get('API_PORT', 4000))
}