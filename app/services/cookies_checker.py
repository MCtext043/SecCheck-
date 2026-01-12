"""
Проверка безопасности cookies
"""
from typing import List
from app.models.security_result import CheckResult
from app.services.base_checker import BaseChecker


class CookiesChecker(BaseChecker):
    """Проверка безопасности cookies"""
    
    def run(self) -> List[CheckResult]:
        """Запускает проверку cookies"""
        if not self._make_request():
            return []
        
        cookies = self.response.cookies
        
        if not cookies:
            return [CheckResult(
                name='Безопасность файлов cookies',
                status='success',
                score=8.0,
                max_score=8.0,
                message='Cookies не используются',
                category='cookies'
            )]
        
        # Собираем Set-Cookie заголовки
        set_cookie_headers = []
        for header_name, header_value in self.response.headers.items():
            if header_name.lower() == 'set-cookie':
                set_cookie_headers.append(header_value)
        
        # Проверяем историю редиректов
        for hist_response in self.response.history:
            for header_name, header_value in hist_response.headers.items():
                if header_name.lower() == 'set-cookie':
                    set_cookie_headers.append(header_value)
        
        if not set_cookie_headers:
            # Используем информацию из объектов cookies
            secure_count = sum(1 for cookie in cookies if cookie.secure)
            total = len(cookies)
            
            score = 4.0 if secure_count == total else 2.0 if secure_count > 0 else 0.0
            
            return [CheckResult(
                name='Безопасность файлов cookies',
                status='success' if score >= 4.0 else 'warning' if score > 0 else 'danger',
                score=score,
                max_score=8.0,
                message=f'Cookies: {total} найдено, Secure: {secure_count}/{total}',
                category='cookies',
                details={'total': total, 'secure': secure_count}
            )]
        
        # Анализируем заголовки
        secure_count = 0
        httponly_count = 0
        samesite_count = 0
        total = len(cookies)
        
        for cookie_header in set_cookie_headers:
            cookie_lower = cookie_header.lower()
            if '; secure' in cookie_lower or cookie_lower.startswith('secure'):
                secure_count += 1
            if '; httponly' in cookie_lower or 'httponly' in cookie_lower:
                httponly_count += 1
            if 'samesite=' in cookie_lower:
                samesite_count += 1
        
        # Рассчитываем оценку
        score = 0.0
        if secure_count == total:
            score += 3.0
        elif secure_count > 0:
            score += 1.5
        
        if httponly_count == total:
            score += 3.0
        elif httponly_count > 0:
            score += 1.5
        
        if samesite_count == total:
            score += 2.0
        elif samesite_count > 0:
            score += 1.0
        
        status = 'success' if score >= 7.0 else 'warning' if score >= 4.0 else 'danger'
        
        return [CheckResult(
            name='Безопасность файлов cookies',
            status=status,
            score=score,
            max_score=8.0,
            message=f'Cookies: {total} найдено, Secure: {secure_count}/{total}, HttpOnly: {httponly_count}/{total}, SameSite: {samesite_count}/{total}',
            category='cookies',
            details={
                'total': total,
                'secure': secure_count,
                'httponly': httponly_count,
                'samesite': samesite_count
            }
        )]

