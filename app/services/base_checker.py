"""
Базовый класс для проверок безопасности
"""
import requests
import warnings
from typing import Dict, List
from app.models.security_result import CheckResult

# Игнорируем предупреждения о небезопасных SSL запросах
warnings.filterwarnings('ignore', message='Unverified HTTPS request')


class BaseChecker:
    """Базовый класс для всех проверок"""
    
    def __init__(self, url: str):
        self.url = url
        self.session = None
        self.response = None
        self.headers = {}
        
    def _make_request(self, timeout: int = 10) -> bool:
        """
        Выполняет HTTP запрос
        
        Returns:
            True если запрос успешен
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
            self.session = requests.Session()
            self.response = self.session.get(
                self.url,
                timeout=timeout,
                verify=False,
                allow_redirects=True,
                headers=headers
            )
            
            # Собираем все заголовки из истории редиректов и финального ответа
            self.headers = {}
            for hist_response in self.response.history:
                for k, v in hist_response.headers.items():
                    k_lower = k.lower()
                    if k_lower not in self.headers:
                        self.headers[k_lower] = v
            
            # Добавляем заголовки финального ответа (приоритет)
            for k, v in self.response.headers.items():
                self.headers[k.lower()] = v
            
            return True
        except Exception as e:
            return False
    
    def check_header(self, header_name: str, variants: List[str] = None) -> tuple:
        """
        Проверяет наличие заголовка
        
        Args:
            header_name: Имя заголовка
            variants: Варианты названий заголовка
            
        Returns:
            Кортеж (найден, значение)
        """
        if variants is None:
            variants = [header_name]
        
        for variant in variants:
            variant_lower = variant.lower()
            if variant_lower in self.headers:
                return True, self.headers[variant_lower]
        
        return False, None
    
    def run(self) -> List[CheckResult]:
        """
        Запускает проверки (должен быть переопределен в подклассах)
        
        Returns:
            Список результатов проверок
        """
        raise NotImplementedError("Метод run() должен быть переопределен")

