"""
Инициализация Flask приложения
"""
import os
from flask import Flask

def create_app():
    # Определяем базовую директорию (корень проекта)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
    
    # Регистрация роутов
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app

