"""
Калькулятор оценки безопасности
"""
from typing import List
from app.models.security_result import CheckResult, SecurityReport


def calculate_level(percentage: float) -> tuple:
    """
    Определяет уровень безопасности по проценту
    
    Args:
        percentage: Процент безопасности (0-100)
        
    Returns:
        Кортеж (level, emoji, color_class)
    """
    if percentage >= 90:
        return ('excellent', '🟢', 'success')
    elif percentage >= 75:
        return ('good', '🟡', 'warning')
    elif percentage >= 60:
        return ('satisfactory', '🟠', 'info')
    else:
        return ('low', '🔴', 'danger')


def calculate_category_scores(checks: List[CheckResult]) -> dict:
    """
    Рассчитывает оценки по категориям
    
    Args:
        checks: Список проверок
        
    Returns:
        Словарь с оценками по категориям
    """
    categories = {}
    
    for check in checks:
        category = check.category
        if category not in categories:
            categories[category] = {'score': 0, 'max_score': 0}
        
        categories[category]['score'] += check.score
        categories[category]['max_score'] += check.max_score
    
    # Преобразуем в проценты
    result = {}
    for category, values in categories.items():
        if values['max_score'] > 0:
            result[category] = (values['score'] / values['max_score']) * 100
        else:
            result[category] = 0
    
    return result


def create_report(url: str, checks: List[CheckResult], recommendations: List[str]) -> SecurityReport:
    """
    Создает отчет о безопасности
    
    Args:
        url: Проверяемый URL
        checks: Список проверок
        recommendations: Список рекомендаций
        
    Returns:
        SecurityReport объект
    """
    from datetime import datetime
    
    # Рассчитываем общий балл
    total_score = sum(check.score for check in checks)
    max_score = sum(check.max_score for check in checks)
    
    # Рассчитываем процент
    percentage = (total_score / max_score * 100) if max_score > 0 else 0
    
    # Определяем уровень
    level, _, _ = calculate_level(percentage)
    
    # Рассчитываем оценки по категориям
    categories = calculate_category_scores(checks)
    
    return SecurityReport(
        url=url,
        timestamp=datetime.now(),
        total_score=total_score,
        max_score=max_score,
        percentage=percentage,
        level=level,
        checks=checks,
        recommendations=recommendations,
        categories=categories
    )

