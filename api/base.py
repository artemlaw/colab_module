import logging
import requests
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('API')


def handle_request(max_retries=3, delay_seconds=15):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    response = func(*args, **kwargs)
                    response.raise_for_status()
                    return response
                except requests.RequestException as e:
                    logger.error(f'Неудачный запрос, ошибка: {e}. Повтор через {delay_seconds} секунд.')
                    time.sleep(delay_seconds)
            logger.error(f'Достигнуто максимальное количество попыток ({max_retries}). Прекращение повторных запросов.')
            return None
        return wrapper
    return decorator


class ApiBase:
    def __init__(self):
        self.headers = {'Content-Type': 'application/json'}

    @handle_request()
    def get_data(self, url, params=None):
        return requests.get(url, headers=self.headers, params=params)

    @handle_request()
    def post_data(self, url, data):
        return requests.post(url, headers=self.headers, json=data)

    @handle_request()
    def put_data(self, url, data):
        return requests.put(url, headers=self.headers, json=data)

    @handle_request()
    def delete_data(self, url):
        return requests.delete(url, headers=self.headers)