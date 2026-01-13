"""
Утилиты для нормализации URL
"""
from urllib.parse import urlparse, urlunparse


def normalize_url(url: str) -> str:
    """
    Нормализует URL, добавляя протокол если отсутствует
    
    Args:
        url: URL для нормализации
        
    Returns:
        Нормализованный URL
    """
    url = url.strip()
    
    # Удаляем пробелы
    url = url.replace(' ', '')
    
    # Если нет протокола, добавляем https://
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Парсим и собираем обратно для нормализации
    parsed = urlparse(url)
    
    # Убираем фрагмент (#)
    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        parsed.query,
        ''  # Убираем fragment
    ))
    
    return normalized


def is_valid_url(url: str) -> bool:
    """
    Проверяет валидность URL
    
    Args:
        url: URL для проверки
        
    Returns:
        True если URL валиден
    """
    try:
        parsed = urlparse(url)
        return all([parsed.scheme, parsed.netloc])
    except Exception:
        return False


