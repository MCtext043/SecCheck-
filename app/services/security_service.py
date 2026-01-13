"""
Главный сервис для проверки безопасности
"""
from typing import List
from app.models.security_result import CheckResult, SecurityReport
from app.services.connection_checker import ConnectionChecker
from app.services.headers_checker import HeadersChecker
from app.services.server_info_checker import ServerInfoChecker
from app.services.cookies_checker import CookiesChecker
from app.services.content_checker import ContentChecker
from app.utils.score_calculator import create_report
from app.utils.url_validator import check_url_exists


class SecurityService:
    """Главный сервис для проверки безопасности сайта"""
    
    def __init__(self, url: str):
        self.url = url
        self.checkers = [
            ConnectionChecker(url),
            HeadersChecker(url),
            ServerInfoChecker(url),
            CookiesChecker(url),
            ContentChecker(url)
        ]
    
    def run_all_checks(self) -> SecurityReport:
        """
        Запускает все проверки безопасности
        
        Returns:
            SecurityReport с результатами
        """
        # Сначала проверяем существование URL
        exists, status_code, error_message = check_url_exists(self.url)
        
        if not exists:
            # Если страница не существует, возвращаем отчет с ошибкой
            error_check = CheckResult(
                name='Доступность сайта',
                status='danger',
                score=0.0,
                max_score=0.0,
                message=error_message,
                category='general',
                details={'error': True, 'status_code': status_code}
            )
            
            return create_report(
                self.url,
                [error_check],
                [f'❌ Сайт недоступен: {error_message}. Проверьте правильность URL и доступность сайта.']
            )
        
        all_checks = []
        recommendations = []
        
        # Запускаем все проверки
        for checker in self.checkers:
            try:
                checks = checker.run()
                all_checks.extend(checks)
                
                # Собираем рекомендации
                for check in checks:
                    if check.status in ['warning', 'danger'] and 'recommendation' in check.details:
                        recommendations.append(check.details['recommendation'])
                    elif check.status == 'danger' and check.score == 0:
                        # Критические проблемы
                        if 'critical' in check.details:
                            recommendations.append(f'🚨 КРИТИЧНО: {check.name} - требуется немедленное исправление')
                        else:
                            recommendations.append(f'⚠️ ВАЖНО: {check.name} - рекомендуется исправить')
            except Exception as e:
                # Если проверка упала, добавляем ошибку
                all_checks.append(CheckResult(
                    name=f'Ошибка проверки: {checker.__class__.__name__}',
                    status='danger',
                    score=0.0,
                    max_score=0.0,
                    message=f'Ошибка: {str(e)[:100]}',
                    category='general'
                ))
        
        # Создаем отчет
        report = create_report(self.url, all_checks, recommendations)
        
        return report

