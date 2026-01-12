"""
Проверка контента и дополнительных аспектов безопасности
"""
from typing import List
from app.models.security_result import CheckResult
from app.services.base_checker import BaseChecker
from urllib.parse import urlparse


class ContentChecker(BaseChecker):
    """Проверка контента и дополнительных аспектов"""
    
    def run(self) -> List[CheckResult]:
        """Запускает проверки контента"""
        if not self._make_request():
            return []
        
        results = []
        
        # Проверка robots.txt
        robots_result = self._check_robots()
        if robots_result:
            results.append(robots_result)
        
        # Проверка на смешанный контент (требует анализа HTML, упрощенная версия)
        mixed_content_result = self._check_mixed_content()
        if mixed_content_result:
            results.append(mixed_content_result)
        
        # Проверка скорости ответа
        response_time_result = self._check_response_time()
        if response_time_result:
            results.append(response_time_result)
        
        return results
    
    def _check_robots(self) -> CheckResult:
        """Проверяет наличие robots.txt"""
        try:
            parsed = urlparse(self.url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            
            response = self.session.get(robots_url, timeout=5, verify=False)
            if response.status_code == 200:
                return CheckResult(
                    name='Файл robots.txt',
                    status='success',
                    score=2.0,
                    max_score=2.0,
                    message='Файл robots.txt найден',
                    category='content'
                )
        except:
            pass
        
        # Более мягкая оценка: даем 80% баллов даже если файл не найден
        return CheckResult(
            name='Файл robots.txt',
            status='info',
            score=1.6,
            max_score=2.0,
            message='Файл robots.txt не найден (не критично)',
            category='content'
        )
    
    def _check_mixed_content(self) -> CheckResult:
        """Проверяет на смешанный контент (упрощенная версия)"""
        parsed = urlparse(self.url)
        if parsed.scheme != 'https':
            return None
        
        # Проверяем заголовок Content-Security-Policy на наличие upgrade-insecure-requests
        csp = self.headers.get('content-security-policy', '')
        if 'upgrade-insecure-requests' in csp.lower():
            return CheckResult(
                name='Защита от смешанного контента',
                status='success',
                score=3.0,
                max_score=3.0,
                message='Настроена автоматическая замена небезопасных ресурсов',
                category='content'
            )
        
        # Более мягкая оценка: даем 50% баллов даже без upgrade-insecure-requests
        return CheckResult(
            name='Защита от смешанного контента',
            status='warning',
            score=1.5,
            max_score=3.0,
            message='Рекомендуется добавить upgrade-insecure-requests в CSP',
            category='content'
        )
    
    def _check_response_time(self) -> CheckResult:
        """Проверяет время ответа сервера"""
        if hasattr(self.response, 'elapsed'):
            elapsed_ms = self.response.elapsed.total_seconds() * 1000
            
            if elapsed_ms < 500:
                score = 3.0
                status = 'success'
                message = f'Отличная скорость ответа: {elapsed_ms:.0f}мс'
            elif elapsed_ms < 1000:
                score = 2.0
                status = 'success'
                message = f'Хорошая скорость ответа: {elapsed_ms:.0f}мс'
            elif elapsed_ms < 2000:
                score = 1.0
                status = 'warning'
                message = f'Приемлемая скорость ответа: {elapsed_ms:.0f}мс'
            else:
                score = 0.5
                status = 'warning'
                message = f'Медленная скорость ответа: {elapsed_ms:.0f}мс'
            
            return CheckResult(
                name='Скорость ответа сервера',
                status=status,
                score=score,
                max_score=3.0,
                message=message,
                category='content',
                details={'response_time_ms': elapsed_ms}
            )
        
        return None

