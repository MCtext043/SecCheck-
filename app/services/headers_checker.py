"""
Проверка безопасности HTTP заголовков
"""
from typing import List
from app.models.security_result import CheckResult
from app.services.base_checker import BaseChecker


class HeadersChecker(BaseChecker):
    """Проверка безопасности заголовков"""
    
    # Конфигурация проверяемых заголовков с весами
    HEADERS_CONFIG = {
        'Принудительное использование HTTPS (HSTS)': {
            'headers': ['strict-transport-security', 'hsts'],
            'weight': 12.0,
            'category': 'headers',
            'description': 'Настройте принудительное использование защищенного соединения'
        },
        'Защита от встраивания (X-Frame-Options)': {
            'headers': ['x-frame-options'],
            'weight': 8.0,
            'category': 'headers',
            'description': 'Настройте защиту от встраивания вашего сайта в чужие страницы'
        },
        'Защита от подмены типа файлов': {
            'headers': ['x-content-type-options'],
            'weight': 8.0,
            'category': 'headers',
            'description': 'Настройте защиту от подмены типа файлов'
        },
        'Политика безопасности контента (CSP)': {
            'headers': ['content-security-policy', 'x-content-security-policy'],
            'weight': 12.0,
            'category': 'headers',
            'description': 'Настройте политику безопасности контента'
        },
        'Защита от XSS': {
            'headers': ['x-xss-protection'],
            'weight': 5.0,
            'category': 'headers',
            'description': 'Настройте защиту от межсайтовых скриптов'
        },
        'Политика Referrer': {
            'headers': ['referrer-policy'],
            'weight': 5.0,
            'category': 'headers',
            'description': 'Настройте политику передачи информации о переходе'
        },
        'Политика доступа (Permissions-Policy)': {
            'headers': ['permissions-policy', 'feature-policy'],
            'weight': 5.0,
            'category': 'headers',
            'description': 'Настройте политику доступа к функциям браузера'
        }
    }
    
    def run(self) -> List[CheckResult]:
        """Запускает проверки заголовков"""
        if not self._make_request():
            return [CheckResult(
                name='Заголовки безопасности',
                status='danger',
                score=0.0,
                max_score=55.0,
                message='Ошибка при получении ответа от сервера',
                category='headers'
            )]
        
        results = []
        
        for name, config in self.HEADERS_CONFIG.items():
            found, value = self.check_header(config['headers'][0], config['headers'])
            
            if found:
                display_value = value[:80] + '...' if len(value) > 80 else value
                results.append(CheckResult(
                    name=name,
                    status='success',
                    score=config['weight'],
                    max_score=config['weight'],
                    message=f'Настроен: {display_value}',
                    category=config['category'],
                    details={'header_value': value}
                ))
            else:
                # Более мягкая оценка: даем частичные баллы за отсутствующие заголовки
                # Критичные заголовки (HSTS, CSP) - 20% от веса
                # Важные заголовки (X-Frame-Options, X-Content-Type-Options) - 40% от веса
                # Остальные - 50% от веса
                critical_headers = ['Принудительное использование HTTPS (HSTS)', 'Политика безопасности контента (CSP)']
                important_headers = ['Защита от встраивания (X-Frame-Options)', 'Защита от подмены типа файлов']
                
                if name in critical_headers:
                    partial_score = config['weight'] * 0.2
                elif name in important_headers:
                    partial_score = config['weight'] * 0.4
                else:
                    partial_score = config['weight'] * 0.5
                
                results.append(CheckResult(
                    name=name,
                    status='warning',
                    score=partial_score,
                    max_score=config['weight'],
                    message='Отсутствует',
                    category=config['category'],
                    details={'recommendation': config['description']}
                ))
        
        return results

