"""
Роуты Flask приложения
"""
from flask import Blueprint, render_template, request, jsonify
from flasgger import swag_from
from app.services.security_service import SecurityService
from app.utils.url_normalizer import normalize_url, is_valid_url
from app.utils.score_calculator import calculate_level

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')


@main_bp.route('/api/check', methods=['POST'])
def check_security():
    """
    Проверка безопасности одного сайта
    ---
    tags:
      - Security
    summary: Проверка безопасности веб-сайта
    description: Выполняет полную проверку безопасности указанного URL
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description: URL для проверки
        required: true
        schema:
          type: object
          required:
            - url
          properties:
            url:
              type: string
              example: "github.com"
              description: URL сайта для проверки (можно без протокола)
    responses:
      200:
        description: Успешная проверка
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            url:
              type: string
              example: "https://github.com"
            score:
              type: number
              example: 85.5
            max_score:
              type: number
              example: 106.0
            percentage:
              type: number
              example: 80.66
            level:
              type: string
              example: "good"
            color_class:
              type: string
              example: "warning"
            checks:
              type: array
              items:
                type: object
            recommendations:
              type: array
              items:
                type: string
            categories:
              type: object
      400:
        description: Некорректный запрос
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: "URL не указан"
      404:
        description: Сайт недоступен
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: "Сайт недоступен: Страница не найдена (404)"
            url:
              type: string
      500:
        description: Внутренняя ошибка сервера
    """
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL не указан'
            }), 400
        
        # Нормализуем URL
        normalized_url = normalize_url(url)
        
        if not is_valid_url(normalized_url):
            return jsonify({
                'success': False,
                'error': 'Некорректный URL'
            }), 400
        
        # Запускаем проверку
        service = SecurityService(normalized_url)
        report = service.run_all_checks()
        
        # Преобразуем в словарь для JSON
        result = report.to_dict()
        
        # Проверяем, есть ли ошибка доступности
        has_access_error = any(
            check.get('name') == 'Доступность сайта' and 
            check.get('status') == 'danger' 
            for check in result.get('checks', [])
        )
        
        if has_access_error:
            # Если сайт недоступен, возвращаем ошибку
            error_check = next(
                (check for check in result['checks'] if check.get('name') == 'Доступность сайта'),
                None
            )
            error_message = error_check.get('message', 'Сайт недоступен') if error_check else 'Сайт недоступен'
            
            return jsonify({
                'success': False,
                'error': error_message,
                'url': normalized_url
            }), 404
        
        # Добавляем дополнительную информацию
        level, color_class = calculate_level(report.percentage)
        result['level'] = level
        result['color_class'] = color_class
        result['success'] = True
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка при проверке: {str(e)}'
        }), 500


@main_bp.route('/api/check/batch', methods=['POST'])
def check_security_batch():
    """
    Массовая проверка безопасности нескольких сайтов
    ---
    tags:
      - Security
    summary: Массовая проверка безопасности
    description: Выполняет проверку безопасности для списка URL
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description: Список URL для проверки
        required: true
        schema:
          type: object
          required:
            - urls
          properties:
            urls:
              type: array
              items:
                type: string
              example: ["github.com", "google.com", "apple.com"]
              description: Массив URL для проверки
    responses:
      200:
        description: Результаты проверки
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            total:
              type: integer
              example: 3
            results:
              type: array
              items:
                type: object
                properties:
                  url:
                    type: string
                  success:
                    type: boolean
                  score:
                    type: number
                  percentage:
                    type: number
                  error:
                    type: string
      400:
        description: Некорректный запрос
    """
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        
        if not urls or not isinstance(urls, list):
            return jsonify({
                'success': False,
                'error': 'URLs не указаны или не являются массивом'
            }), 400
        
        if len(urls) > 10:
            return jsonify({
                'success': False,
                'error': 'Максимум 10 URL за один запрос'
            }), 400
        
        results = []
        for url in urls:
            try:
                normalized_url = normalize_url(url.strip())
                
                if not is_valid_url(normalized_url):
                    results.append({
                        'url': normalized_url,
                        'success': False,
                        'error': 'Некорректный URL'
                    })
                    continue
                
                service = SecurityService(normalized_url)
                report = service.run_all_checks()
                
                level, color_class = calculate_level(report.percentage)
                
                results.append({
                    'url': normalized_url,
                    'success': True,
                    'score': report.total_score,
                    'max_score': report.max_score,
                    'percentage': report.percentage,
                    'level': level,
                    'color_class': color_class
                })
            except Exception as e:
                results.append({
                    'url': url,
                    'success': False,
                    'error': str(e)[:100]
                })
        
        return jsonify({
            'success': True,
            'total': len(results),
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка при массовой проверке: {str(e)}'
        }), 500


@main_bp.route('/api/checks', methods=['GET'])
def get_available_checks():
    """
    Список всех доступных проверок безопасности
    ---
    tags:
      - Security
    summary: Получить список всех проверок
    description: Возвращает информацию о всех доступных проверках безопасности
    produces:
      - application/json
    responses:
      200:
        description: Список проверок
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            checks:
              type: array
              items:
                type: object
                properties:
                  name:
                    type: string
                    example: "Защищенное соединение (HTTPS)"
                  category:
                    type: string
                    example: "connection"
                  max_score:
                    type: number
                    example: 15.0
                  description:
                    type: string
    """
    checks_info = [
        {
            'name': 'Защищенное соединение (HTTPS)',
            'category': 'connection',
            'max_score': 15.0,
            'description': 'Проверка использования HTTPS протокола'
        },
        {
            'name': 'SSL сертификат',
            'category': 'connection',
            'max_score': 10.0,
            'description': 'Проверка валидности и срока действия SSL сертификата'
        },
        {
            'name': 'Принудительное использование HTTPS (HSTS)',
            'category': 'headers',
            'max_score': 12.0,
            'description': 'Проверка наличия заголовка Strict-Transport-Security'
        },
        {
            'name': 'Защита от встраивания (X-Frame-Options)',
            'category': 'headers',
            'max_score': 8.0,
            'description': 'Проверка защиты от clickjacking атак'
        },
        {
            'name': 'Защита от подмены типа файлов',
            'category': 'headers',
            'max_score': 8.0,
            'description': 'Проверка заголовка X-Content-Type-Options'
        },
        {
            'name': 'Политика безопасности контента (CSP)',
            'category': 'headers',
            'max_score': 12.0,
            'description': 'Проверка Content-Security-Policy заголовка'
        },
        {
            'name': 'Защита от XSS',
            'category': 'headers',
            'max_score': 5.0,
            'description': 'Проверка заголовка X-XSS-Protection'
        },
        {
            'name': 'Политика Referrer',
            'category': 'headers',
            'max_score': 5.0,
            'description': 'Проверка заголовка Referrer-Policy'
        },
        {
            'name': 'Политика доступа (Permissions-Policy)',
            'category': 'headers',
            'max_score': 5.0,
            'description': 'Проверка заголовка Permissions-Policy'
        },
        {
            'name': 'Скрытие информации о сервере',
            'category': 'server',
            'max_score': 10.0,
            'description': 'Проверка отсутствия заголовков Server и X-Powered-By'
        },
        {
            'name': 'Secure флаг в cookies',
            'category': 'cookies',
            'max_score': 3.0,
            'description': 'Проверка использования Secure флага в cookies'
        },
        {
            'name': 'HttpOnly флаг в cookies',
            'category': 'cookies',
            'max_score': 3.0,
            'description': 'Проверка использования HttpOnly флага в cookies'
        },
        {
            'name': 'SameSite атрибут в cookies',
            'category': 'cookies',
            'max_score': 2.0,
            'description': 'Проверка использования SameSite атрибута в cookies'
        },
        {
            'name': 'Наличие robots.txt',
            'category': 'content',
            'max_score': 2.0,
            'description': 'Проверка наличия файла robots.txt'
        },
        {
            'name': 'Защита от смешанного контента',
            'category': 'content',
            'max_score': 3.0,
            'description': 'Проверка отсутствия смешанного HTTP/HTTPS контента'
        },
        {
            'name': 'Скорость ответа сервера',
            'category': 'content',
            'max_score': 3.0,
            'description': 'Проверка времени ответа сервера'
        }
    ]
    
    return jsonify({
        'success': True,
        'total': len(checks_info),
        'checks': checks_info
    })


@main_bp.route('/api/info', methods=['GET'])
def api_info():
    """
    Информация об API
    ---
    tags:
      - System
    summary: Информация об API
    description: Возвращает информацию о версии API и доступных endpoints
    produces:
      - application/json
    responses:
      200:
        description: Информация об API
        schema:
          type: object
          properties:
            name:
              type: string
              example: "Security Checker API"
            version:
              type: string
              example: "1.0.0"
            description:
              type: string
            endpoints:
              type: array
              items:
                type: object
            max_score:
              type: number
              example: 106.0
    """
    return jsonify({
        'name': 'Security Checker API',
        'version': '1.0.0',
        'description': 'REST API для проверки безопасности веб-сайтов',
        'max_score': 106.0,
        'endpoints': [
            {
                'path': '/api/check',
                'method': 'POST',
                'description': 'Проверка безопасности одного сайта'
            },
            {
                'path': '/api/check/batch',
                'method': 'POST',
                'description': 'Массовая проверка нескольких сайтов (до 10)'
            },
            {
                'path': '/api/checks',
                'method': 'GET',
                'description': 'Список всех доступных проверок'
            },
            {
                'path': '/api/info',
                'method': 'GET',
                'description': 'Информация об API'
            },
            {
                'path': '/api/health',
                'method': 'GET',
                'description': 'Проверка работоспособности API'
            },
            {
                'path': '/api/docs',
                'method': 'GET',
                'description': 'Swagger документация'
            }
        ]
    })


@main_bp.route('/api/health', methods=['GET'])
def health():
    """
    Проверка работоспособности API
    ---
    tags:
      - System
    summary: Health check
    description: Проверка работоспособности API сервиса
    produces:
      - application/json
    responses:
      200:
        description: API работает
        schema:
          type: object
          properties:
            status:
              type: string
              example: "ok"
    """
    return jsonify({'status': 'ok'})
