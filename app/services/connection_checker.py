"""
Проверка соединения и SSL
"""
import ssl
import socket
from datetime import datetime
from typing import List
from app.models.security_result import CheckResult
from app.services.base_checker import BaseChecker
from urllib.parse import urlparse


class ConnectionChecker(BaseChecker):
    """Проверка соединения и SSL сертификата"""
    
    def run(self) -> List[CheckResult]:
        """Запускает проверки соединения"""
        results = []
        
        # Проверка HTTPS
        parsed = urlparse(self.url)
        is_https = parsed.scheme == 'https'
        
        if is_https:
            results.append(CheckResult(
                name='Защищенное соединение (HTTPS)',
                status='success',
                score=15.0,
                max_score=15.0,
                message='Сайт использует защищенное соединение',
                category='connection'
            ))
            
            # Проверка SSL сертификата
            ssl_result = self._check_ssl_certificate(parsed.hostname, parsed.port or 443)
            results.append(ssl_result)
        else:
            results.append(CheckResult(
                name='Защищенное соединение (HTTPS)',
                status='danger',
                score=0.0,
                max_score=15.0,
                message='Сайт не использует защищенное соединение',
                category='connection',
                details={'critical': True}
            ))
        
        return results
    
    def _check_ssl_certificate(self, hostname: str, port: int) -> CheckResult:
        """Проверяет SSL сертификат"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Проверка срока действия
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (not_after - datetime.now()).days
                    
                    if days_until_expiry > 30:
                        return CheckResult(
                            name='Сертификат безопасности',
                            status='success',
                            score=10.0,
                            max_score=10.0,
                            message=f'Сертификат действителен до {not_after.strftime("%d.%m.%Y")}',
                            category='connection',
                            details={'expiry_date': not_after.isoformat(), 'days_left': days_until_expiry}
                        )
                    elif days_until_expiry > 0:
                        return CheckResult(
                            name='Сертификат безопасности',
                            status='warning',
                            score=7.0,
                            max_score=10.0,
                            message=f'Сертификат скоро истечет (через {days_until_expiry} дней)',
                            category='connection',
                            details={'expiry_date': not_after.isoformat(), 'days_left': days_until_expiry}
                        )
                    else:
                        return CheckResult(
                            name='Сертификат безопасности',
                            status='danger',
                            score=0.0,
                            max_score=10.0,
                            message='Сертификат истек',
                            category='connection',
                            details={'critical': True}
                        )
        except Exception as e:
            return CheckResult(
                name='Сертификат безопасности',
                status='danger',
                score=0.0,
                max_score=10.0,
                message=f'Ошибка проверки: {str(e)[:50]}',
                category='connection',
                details={'error': str(e)}
            )


