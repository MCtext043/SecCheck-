"""
Роуты Flask приложения
"""
from flask import Blueprint, render_template, request, jsonify
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
    """API endpoint для проверки безопасности"""
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


@main_bp.route('/api/health')
def health():
    """Проверка работоспособности API"""
    return jsonify({'status': 'ok'})

