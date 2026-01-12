"""
Проверка раскрытия информации о сервере
"""
from typing import List
from app.models.security_result import CheckResult
from app.services.base_checker import BaseChecker


class ServerInfoChecker(BaseChecker):
    """Проверка раскрытия информации о сервере"""
    
    def run(self) -> List[CheckResult]:
        """Запускает проверку информации о сервере"""
        if not self._make_request():
            return []
        
        server_info = []
        if 'server' in self.headers:
            server_info.append(f"Server: {self.headers['server']}")
        if 'x-powered-by' in self.headers:
            server_info.append(f"X-Powered-By: {self.headers['x-powered-by']}")
        
        if server_info:
            return [CheckResult(
                name='Скрытие информации о сервере',
                status='warning',
                score=5.0,
                max_score=10.0,
                message=f'Обнаружена информация: {", ".join(server_info)}',
                category='server',
                details={'disclosed_info': server_info}
            )]
        else:
            return [CheckResult(
                name='Скрытие информации о сервере',
                status='success',
                score=10.0,
                max_score=10.0,
                message='Информация о сервере скрыта',
                category='server'
            )]

