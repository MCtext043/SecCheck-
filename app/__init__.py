"""
Инициализация Flask приложения
"""
import os
from flask import Flask
from flasgger import Swagger

def create_app():
    # Определяем базовую директорию (корень проекта)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
    
    # Настройка Swagger
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs"
    }
    
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "API Анализатора безопасности веб-сайтов",
            "description": "REST API для проверки безопасности веб-сайтов",
            "version": "1.0.0",
            "contact": {
                "name": "Security Checker API"
            }
        },
        "basePath": "/",
        "schemes": ["http", "https"],
        "tags": [
            {
                "name": "Security",
                "description": "Проверка безопасности сайтов"
            },
            {
                "name": "System",
                "description": "Системные endpoints"
            }
        ]
    }
    
    swagger = Swagger(app, config=swagger_config, template=swagger_template)
    
    # Регистрация роутов
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app

