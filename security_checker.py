#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Консольное приложение для оценки безопасности веб-сайтов
"""

import requests
import ssl
import socket
from urllib.parse import urlparse
from datetime import datetime
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')


class SecurityChecker:
    """Класс для проверки безопасности веб-сайта"""
    
    def __init__(self, url):
        self.url = self._normalize_url(url)
        self.results = {}
        self.score = 0
        self.max_score = 0
        self.recommendations = []
    
    def _normalize_url(self, url):
        """Нормализует URL, добавляя протокол если отсутствует"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    def check_https(self):
        """Проверка использования HTTPS"""
        parsed = urlparse(self.url)
        is_https = parsed.scheme == 'https'
        
        if is_https:
            self.score += 20
            self.results['Защищенное соединение (HTTPS)'] = {'status': '✓', 'score': 20, 'message': 'Сайт использует защищенное соединение'}
        else:
            self.results['Защищенное соединение (HTTPS)'] = {'status': '✗', 'score': 0, 'message': 'Сайт не использует защищенное соединение'}
            self.recommendations.append('⚠️ ВАЖНО: Настройте защищенное соединение (HTTPS) - это шифрует данные между пользователем и сайтом, защищая пароли и личную информацию')
        
        self.max_score += 20
        return is_https
    
    def check_ssl_certificate(self):
        """Проверка валидности SSL сертификата"""
        parsed = urlparse(self.url)
        hostname = parsed.hostname
        port = parsed.port or 443
        
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    issuer = dict(x[0] for x in cert['issuer'])
                    subject = dict(x[0] for x in cert['subject'])
                    
                    # Проверка срока действия
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (not_after - datetime.now()).days
                    
                    if days_until_expiry > 30:
                        self.score += 15
                        self.results['Сертификат безопасности'] = {
                            'status': '✓',
                            'score': 15,
                            'message': f'Сертификат безопасности действителен до {not_after.strftime("%d.%m.%Y")}'
                        }
                    elif days_until_expiry > 0:
                        self.score += 10
                        self.results['Сертификат безопасности'] = {
                            'status': '⚠',
                            'score': 10,
                            'message': f'Сертификат безопасности скоро истечет (через {days_until_expiry} дней)'
                        }
                        self.recommendations.append('⚠️ Обновите сертификат безопасности до истечения срока - иначе браузеры будут показывать предупреждение пользователям')
                    else:
                        self.results['Сертификат безопасности'] = {
                            'status': '✗',
                            'score': 0,
                            'message': 'Сертификат безопасности истек'
                        }
                        self.recommendations.append('🚨 КРИТИЧНО: Сертификат безопасности истек! Немедленно обновите его - иначе браузеры будут блокировать доступ к сайту')
                    
                    self.max_score += 15
                    return True
        except Exception as e:
            self.results['Сертификат безопасности'] = {
                'status': '✗',
                'score': 0,
                'message': f'Ошибка проверки сертификата: {str(e)}'
            }
            self.recommendations.append('🚨 КРИТИЧНО: Проблема с сертификатом безопасности - проверьте настройки сервера')
            self.max_score += 15
            return False
    
    def check_security_headers(self):
        """Проверка безопасности HTTP заголовков"""
        try:
            session = requests.Session()
            response = session.get(self.url, timeout=10, verify=False, allow_redirects=True)
            
            # Собираем все заголовки из финального ответа и истории редиректов
            all_headers = {}
            for hist_response in response.history:
                for k, v in hist_response.headers.items():
                    k_lower = k.lower()
                    if k_lower not in all_headers:
                        all_headers[k_lower] = v
            
            # Добавляем заголовки финального ответа (они имеют приоритет)
            for k, v in response.headers.items():
                all_headers[k.lower()] = v
            
            security_headers = {
                'Принудительное использование HTTPS': {
                    'headers': ['strict-transport-security', 'hsts'],
                    'weight': 15,
                    'description': 'Настройте принудительное использование защищенного соединения - это предотвращает перехват данных злоумышленниками'
                },
                'Защита от встраивания в чужие страницы': {
                    'headers': ['x-frame-options'],
                    'weight': 10,
                    'description': 'Настройте защиту от встраивания вашего сайта в чужие страницы - это защищает от мошеннических схем'
                },
                'Защита от подмены типа файлов': {
                    'headers': ['x-content-type-options'],
                    'weight': 10,
                    'description': 'Настройте защиту от подмены типа файлов - это предотвращает выполнение вредоносного кода'
                },
                'Политика безопасности контента': {
                    'headers': ['content-security-policy', 'x-content-security-policy'],
                    'weight': 15,
                    'description': 'Настройте политику безопасности контента - это защищает от внедрения вредоносного кода на страницы'
                },
                'Защита от межсайтовых скриптов': {
                    'headers': ['x-xss-protection'],
                    'weight': 5,
                    'description': 'Настройте защиту от межсайтовых скриптов - это предотвращает кражу данных пользователей'
                },
                'Политика передачи информации о переходе': {
                    'headers': ['referrer-policy'],
                    'weight': 5,
                    'description': 'Настройте политику передачи информации о переходе - это защищает приватность пользователей'
                },
                'Политика доступа к функциям браузера': {
                    'headers': ['permissions-policy', 'feature-policy'],
                    'weight': 5,
                    'description': 'Настройте политику доступа к функциям браузера (камера, микрофон и т.д.) - это защищает от несанкционированного доступа'
                }
            }
            
            for name, config in security_headers.items():
                header_variants = config['headers']
                weight = config['weight']
                
                found = False
                found_value = None
                
                for header_variant in header_variants:
                    if header_variant in all_headers:
                        found = True
                        found_value = all_headers[header_variant]
                        break
                
                if found:
                    self.score += weight
                    # Обрезаем длинные значения заголовков для читаемости
                    display_value = found_value[:80] + '...' if len(found_value) > 80 else found_value
                    self.results[name] = {
                        'status': '✓',
                        'score': weight,
                        'message': f'Настроен: {display_value}'
                    }
                else:
                    self.results[name] = {
                        'status': '✗',
                        'score': 0,
                        'message': 'Отсутствует'
                    }
                    self.recommendations.append(f'💡 {config["description"]}')
                
                self.max_score += weight
            
            return True
        except Exception as e:
            self.results['Заголовки безопасности'] = {
                'status': '✗',
                'score': 0,
                'message': f'Ошибка проверки: {str(e)}'
            }
            self.max_score += 65
            return False
    
    def check_server_info_disclosure(self):
        """Проверка на раскрытие информации о сервере"""
        try:
            response = requests.get(self.url, timeout=10, verify=False, allow_redirects=True)
            headers = response.headers
            
            server_info = []
            if 'Server' in headers:
                server_info.append(f"Server: {headers['Server']}")
            if 'X-Powered-By' in headers:
                server_info.append(f"X-Powered-By: {headers['X-Powered-By']}")
            
            if server_info:
                self.results['Скрытие информации о сервере'] = {
                    'status': '⚠',
                    'score': 5,
                    'message': f'Обнаружена информация о сервере: {", ".join(server_info)}'
                }
                self.recommendations.append('💡 Скрывайте информацию о сервере - злоумышленники могут использовать её для поиска уязвимостей')
            else:
                self.score += 10
                self.results['Скрытие информации о сервере'] = {
                    'status': '✓',
                    'score': 10,
                    'message': 'Информация о сервере скрыта'
                }
            
            self.max_score += 10
            return True
        except Exception as e:
            self.max_score += 10
            return False
    
    def check_cookie_security(self):
        """Проверка безопасности cookies"""
        try:
            # Используем сессию для получения всех заголовков, включая редиректы
            session = requests.Session()
            response = session.get(self.url, timeout=10, verify=False, allow_redirects=True)
            cookies = response.cookies
            
            if not cookies:
                self.results['Безопасность файлов cookies'] = {
                    'status': '✓',
                    'score': 5,
                    'message': 'Файлы cookies не используются'
                }
                self.score += 5
                self.max_score += 5
                return True
            
            secure_count = 0
            httponly_count = 0
            samesite_count = 0
            
            # Собираем все Set-Cookie заголовки из всех ответов (включая редиректы)
            set_cookie_headers = []
            
            # Проверяем основной ответ
            for header_name, header_value in response.headers.items():
                if header_name.lower() == 'set-cookie':
                    set_cookie_headers.append(header_value)
            
            # Проверяем историю редиректов
            for hist_response in response.history:
                for header_name, header_value in hist_response.headers.items():
                    if header_name.lower() == 'set-cookie':
                        set_cookie_headers.append(header_value)
            
            # Если заголовки не найдены, используем информацию из объектов cookies
            if not set_cookie_headers:
                # Проверяем через атрибуты cookie объектов
                for cookie in cookies:
                    if cookie.secure:
                        secure_count += 1
                    # HttpOnly и SameSite не всегда доступны через cookie объект
                    # В этом случае считаем, что они могут отсутствовать
            else:
                # Анализируем Set-Cookie заголовки
                for cookie_header in set_cookie_headers:
                    cookie_lower = cookie_header.lower()
                    if '; secure' in cookie_lower or cookie_lower.startswith('secure'):
                        secure_count += 1
                    if '; httponly' in cookie_lower or 'httponly' in cookie_lower:
                        httponly_count += 1
                    if 'samesite=' in cookie_lower:
                        samesite_count += 1
            
            # Дополнительная проверка через cookie объекты для Secure
            if not set_cookie_headers:
                for cookie in cookies:
                    if cookie.secure:
                        secure_count += 1
            
            total_cookies = len(cookies)
            score = 0
            
            # Нормализуем счетчики относительно общего количества cookies
            if total_cookies > 0:
                if secure_count == total_cookies:
                    score += 2
                elif secure_count > 0:
                    score += 1
                    self.recommendations.append('💡 Настройте передачу cookies только по защищенному соединению (Secure) - это защищает от перехвата')
                else:
                    self.recommendations.append('🚨 КРИТИЧНО: Настройте передачу cookies только по защищенному соединению (Secure) - иначе злоумышленники могут их украсть')
                
                if httponly_count == total_cookies:
                    score += 2
                elif httponly_count > 0:
                    score += 1
                    self.recommendations.append('💡 Настройте защиту cookies от доступа через JavaScript (HttpOnly) - это защищает от кражи через вредоносный код')
                else:
                    self.recommendations.append('🚨 КРИТИЧНО: Настройте защиту cookies от доступа через JavaScript (HttpOnly) - иначе вредоносный код может украсть сессию пользователя')
                
                if samesite_count == total_cookies:
                    score += 1
                elif samesite_count > 0:
                    score += 0.5
                    self.recommendations.append('💡 Настройте ограничение отправки cookies только с вашего сайта (SameSite) - это защищает от подделки запросов')
                else:
                    self.recommendations.append('💡 Настройте ограничение отправки cookies только с вашего сайта (SameSite) - это защищает от подделки запросов от имени пользователя')
            
            self.score += int(score)
            self.max_score += 5
            
            self.results['Безопасность файлов cookies'] = {
                'status': '✓' if score == 5 else '⚠' if score > 0 else '✗',
                'score': int(score),
                'message': f'Найдено файлов: {total_cookies}, защищенных: {secure_count}/{total_cookies}, недоступных для JavaScript: {httponly_count}/{total_cookies}, с ограничением домена: {samesite_count}/{total_cookies}'
            }
            
            return True
        except Exception as e:
            self.results['Безопасность файлов cookies'] = {
                'status': '✗',
                'score': 0,
                'message': f'Ошибка проверки: {str(e)}'
            }
            self.max_score += 5
            return False
    
    def run_all_checks(self):
        """Запуск всех проверок"""
        print(f"\n🔍 Проверка безопасности сайта: {self.url}\n")
        print("=" * 60)
        
        self.check_https()
        if self.results.get('Защищенное соединение (HTTPS)', {}).get('status') == '✓':
            self.check_ssl_certificate()
        self.check_security_headers()
        self.check_server_info_disclosure()
        self.check_cookie_security()
        
        return self.generate_report()
    
    def generate_report(self):
        """Генерация отчета о безопасности"""
        print("\n📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ:\n")
        print("-" * 60)
        
        for check_name, result in self.results.items():
            status = result['status']
            score = result['score']
            message = result['message']
            print(f"{status} {check_name}: {message} (+{score} баллов)")
        
        print("-" * 60)
        
        # Расчет итогового балла
        final_score = int((self.score / self.max_score) * 100) if self.max_score > 0 else 0
        
        print(f"\n🎯 ИТОГОВАЯ ОЦЕНКА БЕЗОПАСНОСТИ: {final_score}/100\n")
        
        # Оценка уровня безопасности
        if final_score >= 85:
            level = "ОТЛИЧНО"
            emoji = "🟢"
        elif final_score >= 70:
            level = "ХОРОШО"
            emoji = "🟡"
        elif final_score >= 50:
            level = "УДОВЛЕТВОРИТЕЛЬНО"
            emoji = "🟠"
        else:
            level = "НИЗКО"
            emoji = "🔴"
        
        print(f"{emoji} Уровень безопасности: {level}")
        
        # Рекомендации
        if self.recommendations:
            print("\n💡 РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ БЕЗОПАСНОСТИ:\n")
            for i, rec in enumerate(self.recommendations, 1):
                print(f"{i}. {rec}")
        else:
            print("\n✅ Критических проблем не обнаружено!")
        
        print("\n" + "=" * 60)
        
        return final_score


def main():
    """Главная функция приложения"""
    print("=" * 60)
    print("🔒 АНАЛИЗАТОР БЕЗОПАСНОСТИ ВЕБ-САЙТОВ")
    print("=" * 60)
    
    while True:
        url = input("\nВведите URL сайта для проверки (или 'exit' для выхода): ").strip()
        
        if url.lower() in ['exit', 'quit', 'выход']:
            print("\nДо свидания!")
            break
        
        if not url:
            print("❌ Пожалуйста, введите корректный URL")
            continue
        
        try:
            checker = SecurityChecker(url)
            checker.run_all_checks()
        except KeyboardInterrupt:
            print("\n\nПрервано пользователем")
            break
        except Exception as e:
            print(f"\n❌ Ошибка при проверке: {str(e)}")
        
        print("\n")


if __name__ == "__main__":
    main()

