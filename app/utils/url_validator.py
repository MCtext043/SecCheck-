"""
Валидация URL на доступность
"""
import requests
import warnings

warnings.filterwarnings('ignore', message='Unverified HTTPS request')


def check_url_exists(url: str, timeout: int = 10) -> tuple:
    """
    Проверяет существование и доступность URL
    
    Args:
        url: URL для проверки
        timeout: Таймаут запроса в секундах
        
    Returns:
        Кортеж (существует, статус_код, сообщение_об_ошибке)
    """
    # Заголовки для имитации обычного браузера
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        response = requests.get(
            url,
            timeout=timeout,
            verify=False,
            allow_redirects=True,
            headers=headers
        )
        
        # Проверяем статус код
        if response.status_code >= 400:
            # Нестандартные коды, которые могут означать блокировку, но сайт доступен
            if response.status_code in [498, 499]:
                # Коды 498/499 часто означают блокировку ботов, но сайт технически доступен
                # Продолжаем проверку, но с предупреждением
                return True, response.status_code, f'Сайт доступен, но может блокировать автоматические запросы ({response.status_code})'
            elif response.status_code == 404:
                return False, response.status_code, 'Страница не найдена (404)'
            elif response.status_code == 403:
                return False, response.status_code, 'Доступ запрещен (403). Сайт может блокировать автоматические запросы'
            elif response.status_code >= 500:
                return False, response.status_code, f'Ошибка сервера ({response.status_code})'
            else:
                # Для других 4xx кодов - считаем что сайт недоступен
                return False, response.status_code, f'Ошибка доступа ({response.status_code})'
        
        # Если статус код 200-399, считаем что страница существует
        return True, response.status_code, 'OK'
        
    except requests.exceptions.Timeout:
        return False, None, 'Превышено время ожидания ответа от сервера'
    except requests.exceptions.ConnectionError:
        return False, None, 'Не удалось подключиться к серверу. Проверьте правильность URL'
    except requests.exceptions.TooManyRedirects:
        return False, None, 'Слишком много редиректов'
    except requests.exceptions.RequestException as e:
        return False, None, f'Ошибка при запросе: {str(e)[:100]}'
    except Exception as e:
        return False, None, f'Неожиданная ошибка: {str(e)[:100]}'

