"""
Модель результата проверки безопасности
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class CheckResult:
    """Результат одной проверки"""
    name: str
    status: str  # 'success', 'warning', 'danger', 'info'
    score: float
    max_score: float
    message: str
    details: Dict = field(default_factory=dict)
    category: str = 'general'  # 'connection', 'headers', 'cookies', 'server', 'content'


@dataclass
class SecurityReport:
    """Полный отчет о безопасности"""
    url: str
    timestamp: datetime
    total_score: float
    max_score: float
    percentage: float
    level: str  # 'excellent', 'good', 'satisfactory', 'low'
    checks: List[CheckResult] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    categories: Dict[str, float] = field(default_factory=dict)  # Оценки по категориям
    
    def to_dict(self):
        """Преобразование в словарь для JSON"""
        return {
            'url': self.url,
            'timestamp': self.timestamp.isoformat(),
            'score': round(self.total_score, 1),
            'max_score': round(self.max_score, 1),
            'percentage': round(self.percentage, 1),
            'level': self.level,
            'checks': [
                {
                    'name': check.name,
                    'status': check.status,
                    'score': check.score,
                    'max_score': check.max_score,
                    'message': check.message,
                    'details': check.details,
                    'category': check.category
                }
                for check in self.checks
            ],
            'recommendations': self.recommendations,
            'categories': {k: round(v, 1) for k, v in self.categories.items()}
        }


