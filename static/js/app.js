// Глобальные переменные для графиков
let categoryChart = null;
let statusChart = null;

// Обработка формы
document.getElementById('checkForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const urlInput = document.getElementById('urlInput');
    const checkButton = document.getElementById('checkButton');
    const buttonText = checkButton.querySelector('.button-text');
    const spinner = checkButton.querySelector('.spinner-border');
    const resultsContainer = document.getElementById('resultsContainer');
    const errorContainer = document.getElementById('errorContainer');
    
    const url = urlInput.value.trim();
    
    if (!url) {
        showError('Пожалуйста, введите URL сайта');
        return;
    }
    
    // Показываем загрузку
    checkButton.disabled = true;
    buttonText.classList.add('d-none');
    spinner.classList.remove('d-none');
    resultsContainer.classList.add('d-none');
    errorContainer.classList.add('d-none');
    
    try {
        const response = await fetch('/api/check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data);
        } else {
            // Проверяем, является ли это ошибкой доступности
            if (response.status === 404 || data.error?.includes('не найден') || data.error?.includes('недоступен')) {
                showError(`❌ Сайт недоступен: ${data.error || 'Страница не существует'}. Проверьте правильность URL и убедитесь, что сайт доступен.`);
            } else {
                showError(data.error || 'Произошла ошибка при проверке сайта');
            }
        }
    } catch (error) {
        showError('Ошибка соединения с сервером: ' + error.message);
    } finally {
        // Скрываем загрузку
        checkButton.disabled = false;
        buttonText.classList.remove('d-none');
        spinner.classList.add('d-none');
    }
});

function displayResults(data) {
    const resultsContainer = document.getElementById('resultsContainer');
    
    // Обновляем счет
    updateScore(data);
    
    // Обновляем время проверки
    const checkTime = document.getElementById('checkTime');
    const timestamp = new Date(data.timestamp);
    checkTime.textContent = timestamp.toLocaleString('ru-RU');
    
    // Создаем графики
    createCharts(data);
    
    // Отображаем проверки
    displayChecks(data.checks);
    
    // Отображаем рекомендации
    displayRecommendations(data.recommendations);
    
    // Показываем контейнер
    resultsContainer.classList.remove('d-none');
    resultsContainer.classList.add('results-wrapper');
    
    // Прокручиваем к результатам
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function updateScore(data) {
    const scoreValue = document.getElementById('scoreValue');
    const levelText = document.getElementById('levelText');
    const levelDescription = document.getElementById('levelDescription');
    const scoreCircle = document.getElementById('scoreCircle');
    const scoreRing = document.getElementById('scoreRing');
    
    // Анимируем счет
    animateScore(data.percentage, scoreValue);
    
    // Обновляем кольцо прогресса
    const circumference = 2 * Math.PI * 90; // радиус = 90
    const offset = circumference - (data.percentage / 100) * circumference;
    scoreRing.style.strokeDashoffset = offset;
    
    // Вычисляем цвет на основе процента (плавный переход от красного к зеленому)
    const color = getColorByPercentage(data.percentage);
    scoreRing.style.stroke = color.ring;
    scoreCircle.style.background = color.circle;
    
    // Обновляем уровень
    const levelTexts = {
        'excellent': '🟢 Отличный уровень безопасности',
        'good': '🟡 Хороший уровень безопасности',
        'satisfactory': '🟠 Удовлетворительный уровень',
        'low': '🔴 Низкий уровень безопасности'
    };
    
    const descriptions = {
        'excellent': 'Ваш сайт имеет отличную защиту. Все основные параметры безопасности настроены правильно.',
        'good': 'Хороший уровень безопасности. Есть несколько моментов, которые можно улучшить.',
        'satisfactory': 'Удовлетворительный уровень. Рекомендуется улучшить некоторые аспекты безопасности.',
        'low': 'Низкий уровень безопасности. Требуется срочное улучшение защитных настроек.'
    };
    
    levelText.textContent = levelTexts[data.level] || levelTexts['low'];
    levelDescription.textContent = descriptions[data.level] || descriptions['low'];
}

// Функция для плавного перехода цвета от красного к зеленому
function getColorByPercentage(percentage) {
    // Нормализуем процент от 0 до 1
    const normalized = Math.max(0, Math.min(100, percentage)) / 100;
    
    // Интерполируем между красным и зеленым
    // Красный: rgb(239, 68, 68) = #ef4444
    // Желтый: rgb(245, 158, 11) = #f59e0b (при 50%)
    // Зеленый: rgb(16, 185, 129) = #10b981
    
    let r, g, b;
    
    if (normalized < 0.5) {
        // От красного к желтому (0% - 50%)
        const t = normalized * 2; // 0-1 в диапазоне 0-50%
        r = Math.round(239 + (245 - 239) * t);
        g = Math.round(68 + (158 - 68) * t);
        b = Math.round(68 + (11 - 68) * t);
    } else {
        // От желтого к зеленому (50% - 100%)
        const t = (normalized - 0.5) * 2; // 0-1 в диапазоне 50-100%
        r = Math.round(245 + (16 - 245) * t);
        g = Math.round(158 + (185 - 158) * t);
        b = Math.round(11 + (129 - 11) * t);
    }
    
    const hexColor = `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    
    // Создаем градиент для круга
    const gradient = `linear-gradient(135deg, ${hexColor} 0%, ${darkenColor(hexColor, 10)} 100%)`;
    
    return {
        ring: hexColor,
        circle: gradient
    };
}

// Функция для затемнения цвета
function darkenColor(hex, percent) {
    const num = parseInt(hex.replace('#', ''), 16);
    const r = Math.max(0, Math.min(255, (num >> 16) - percent));
    const g = Math.max(0, Math.min(255, ((num >> 8) & 0x00FF) - percent));
    const b = Math.max(0, Math.min(255, (num & 0x0000FF) - percent));
    return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')}`;
}

function animateScore(targetScore, element) {
    let currentScore = 0;
    const increment = targetScore / 50;
    const timer = setInterval(() => {
        currentScore += increment;
        if (currentScore >= targetScore) {
            currentScore = targetScore;
            clearInterval(timer);
        }
        element.textContent = Math.round(currentScore);
    }, 20);
}

function createCharts(data) {
    // График по категориям
    const categoryCtx = document.getElementById('categoryChart').getContext('2d');
    
    if (categoryChart) {
        categoryChart.destroy();
    }
    
    const categories = Object.keys(data.categories);
    const categoryScores = Object.values(data.categories);
    
    categoryChart = new Chart(categoryCtx, {
        type: 'bar',
        data: {
            labels: categories.map(cat => {
                const names = {
                    'connection': 'Соединение',
                    'headers': 'Заголовки',
                    'cookies': 'Cookies',
                    'server': 'Сервер',
                    'content': 'Контент'
                };
                return names[cat] || cat;
            }),
            datasets: [{
                label: 'Оценка (%)',
                data: categoryScores,
                backgroundColor: [
                    'rgba(25, 135, 84, 0.8)',
                    'rgba(13, 110, 253, 0.8)',
                    'rgba(255, 193, 7, 0.8)',
                    'rgba(220, 53, 69, 0.8)',
                    'rgba(13, 202, 240, 0.8)'
                ],
                borderColor: [
                    'rgba(25, 135, 84, 1)',
                    'rgba(13, 110, 253, 1)',
                    'rgba(255, 193, 7, 1)',
                    'rgba(220, 53, 69, 1)',
                    'rgba(13, 202, 240, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
    
    // График распределения статусов
    const statusCtx = document.getElementById('statusChart').getContext('2d');
    
    if (statusChart) {
        statusChart.destroy();
    }
    
    const statusCounts = {
        success: 0,
        warning: 0,
        danger: 0,
        info: 0
    };
    
    data.checks.forEach(check => {
        if (statusCounts.hasOwnProperty(check.status)) {
            statusCounts[check.status]++;
        }
    });
    
    statusChart = new Chart(statusCtx, {
        type: 'doughnut',
        data: {
            labels: ['Успешно', 'Предупреждение', 'Опасность', 'Информация'],
            datasets: [{
                data: [
                    statusCounts.success,
                    statusCounts.warning,
                    statusCounts.danger,
                    statusCounts.info
                ],
                backgroundColor: [
                    'rgba(25, 135, 84, 0.8)',
                    'rgba(255, 193, 7, 0.8)',
                    'rgba(220, 53, 69, 0.8)',
                    'rgba(13, 202, 240, 0.8)'
                ],
                borderColor: [
                    'rgba(25, 135, 84, 1)',
                    'rgba(255, 193, 7, 1)',
                    'rgba(220, 53, 69, 1)',
                    'rgba(13, 202, 240, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function displayChecks(checks) {
    const accordion = document.getElementById('checksAccordion');
    accordion.innerHTML = '';
    
    // Группируем по категориям
    const checksByCategory = {};
    checks.forEach(check => {
        if (!checksByCategory[check.category]) {
            checksByCategory[check.category] = [];
        }
        checksByCategory[check.category].push(check);
    });
    
    const categoryNames = {
        'connection': 'Соединение и SSL',
        'headers': 'Заголовки безопасности',
        'cookies': 'Безопасность Cookies',
        'server': 'Информация о сервере',
        'content': 'Контент и производительность',
        'general': 'Общие проверки'
    };
    
    let accordionIndex = 0;
    
    Object.keys(checksByCategory).forEach(category => {
        const categoryChecks = checksByCategory[category];
        
        const categoryCard = document.createElement('div');
        categoryCard.className = 'accordion-item';
        
        const categoryHeader = document.createElement('h2');
        categoryHeader.className = 'accordion-header';
        categoryHeader.id = `heading${accordionIndex}`;
        
        const categoryButton = document.createElement('button');
        categoryButton.className = 'accordion-button';
        categoryButton.type = 'button';
        categoryButton.setAttribute('data-bs-toggle', 'collapse');
        categoryButton.setAttribute('data-bs-target', `#collapse${accordionIndex}`);
        categoryButton.textContent = categoryNames[category] || category;
        
        categoryHeader.appendChild(categoryButton);
        
        const categoryCollapse = document.createElement('div');
        categoryCollapse.id = `collapse${accordionIndex}`;
        categoryCollapse.className = 'accordion-collapse collapse show';
        categoryCollapse.setAttribute('data-bs-parent', '#checksAccordion');
        
        const categoryBody = document.createElement('div');
        categoryBody.className = 'accordion-body';
        
        categoryChecks.forEach(check => {
            const checkItem = createCheckItem(check);
            categoryBody.appendChild(checkItem);
        });
        
        categoryCollapse.appendChild(categoryBody);
        categoryCard.appendChild(categoryHeader);
        categoryCard.appendChild(categoryCollapse);
        accordion.appendChild(categoryCard);
        
        accordionIndex++;
    });
}

function createCheckItem(check) {
    const item = document.createElement('div');
    item.className = `check-item p-3 mb-3 rounded ${check.status}`;
    
    const statusIcons = {
        'success': '<i class="bi bi-check-circle-fill text-success"></i>',
        'warning': '<i class="bi bi-exclamation-triangle-fill text-warning"></i>',
        'danger': '<i class="bi bi-x-circle-fill text-danger"></i>',
        'info': '<i class="bi bi-info-circle-fill text-info"></i>'
    };
    
    const statusBadges = {
        'success': '<span class="status-badge status-success">Успешно</span>',
        'warning': '<span class="status-badge status-warning">Предупреждение</span>',
        'danger': '<span class="status-badge status-danger">Опасность</span>',
        'info': '<span class="status-badge status-info">Информация</span>'
    };
    
    const scoreText = check.score > 0 
        ? `<span class="badge bg-primary ms-2">+${check.score.toFixed(1)}</span>`
        : '';
    
    item.innerHTML = `
        <div class="d-flex justify-content-between align-items-start">
            <div class="flex-grow-1">
                <h6 class="mb-2">
                    ${statusIcons[check.status] || ''} ${check.name}
                    ${scoreText}
                </h6>
                <p class="mb-0 text-muted">${check.message}</p>
            </div>
            <div>
                ${statusBadges[check.status] || ''}
            </div>
        </div>
    `;
    
    return item;
}

function displayRecommendations(recommendations) {
    const recommendationsList = document.getElementById('recommendationsList');
    const recommendationsCard = document.getElementById('recommendationsCard');
    
    if (!recommendations || recommendations.length === 0) {
        recommendationsCard.classList.add('d-none');
        return;
    }
    
    recommendationsCard.classList.remove('d-none');
    recommendationsList.innerHTML = '';
    
    recommendations.forEach(rec => {
        const item = document.createElement('li');
        item.className = 'list-group-item';
        
        const isCritical = rec.includes('🚨') || rec.includes('КРИТИЧНО');
        if (isCritical) {
            item.classList.add('recommendation-item', 'critical');
        } else {
            item.classList.add('recommendation-item');
        }
        
        item.textContent = rec;
        recommendationsList.appendChild(item);
    });
}

function showError(message) {
    const errorContainer = document.getElementById('errorContainer');
    const errorMessage = document.getElementById('errorMessage');
    
    errorMessage.textContent = message;
    errorContainer.classList.remove('d-none');
    
    errorContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

