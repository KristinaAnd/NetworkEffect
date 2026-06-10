// Основной JavaScript файл

// Функция для получения CSRF токена
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Функция для показа уведомлений
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Функция для подтверждения удаления
function confirmDelete(resultId) {
    if (confirm('Вы уверены, что хотите удалить этот результат?')) {
        fetch(`/result/${resultId}/delete/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showNotification('Результат успешно удален', 'success');
                setTimeout(() => location.reload(), 1000);
            } else {
                showNotification('Ошибка при удалении: ' + data.message, 'error');
            }
        })
        .catch(error => {
            showNotification('Ошибка сети: ' + error, 'error');
        });
    }
}

// Функция для экспорта данных
function exportData(resultId, format) {
    window.location.href = `/export/${resultId}/${format}/`;
    showNotification(`Экспорт в ${format.toUpperCase()} начат`, 'success');
}

// Функция для загрузки статистики
function loadDashboardStats() {
    fetch('/api/stats/')
        .then(response => response.json())
        .then(data => {
            // Обновляем статистику на дашборде
            document.querySelectorAll('.stat-value').forEach(el => {
                const type = el.dataset.statType;
                if (type && data[type]) {
                    el.textContent = data[type];
                }
            });
        })
        .catch(error => console.error('Error loading stats:', error));
}

// Функция для валидации формы
function validateGraphForm(formData) {
    const numAgents = parseInt(formData.get('num_agents'));
    const density = parseInt(formData.get('density'));
    const directed = formData.get('directed') === 'directed';
    
    let maxEdges;
    if (directed) {
        maxEdges = numAgents * (numAgents - 1);
    } else {
        maxEdges = numAgents * (numAgents - 1) / 2;
    }
    
    if (density > maxEdges) {
        showNotification(`Количество связей (${density}) превышает максимально возможное (${maxEdges})`, 'error');
        return false;
    }
    
    if (numAgents < 2) {
        showNotification('Количество агентов должно быть не менее 2', 'error');
        return false;
    }
    
    if (numAgents > 100) {
        showNotification('Количество агентов не должно превышать 100', 'error');
        return false;
    }
    
    if (density < 1) {
        showNotification('Количество связей должно быть не менее 1', 'error');
        return false;
    }
    
    return true;
}

// Функция для обновления максимального количества связей
function updateMaxEdges() {
    const numAgentsInput = document.getElementById('num_agents');
    const densityInput = document.getElementById('density');
    const directedRadios = document.querySelectorAll('input[name="directed"]');
    
    if (!numAgentsInput || !densityInput) return;
    
    const numAgents = parseInt(numAgentsInput.value) || 0;
    let directed = false;
    
    directedRadios.forEach(radio => {
        if (radio.checked && radio.value === 'directed') {
            directed = true;
        }
    });
    
    let maxEdges;
    if (directed) {
        maxEdges = numAgents * (numAgents - 1);
    } else {
        maxEdges = numAgents * (numAgents - 1) / 2;
    }
    
    densityInput.max = maxEdges;
    const helpText = document.getElementById('densityHelp');
    if (helpText) {
        helpText.innerHTML = `Максимально возможное: <strong>${maxEdges}</strong>`;
    }
}

// Функция для отображения/скрытия поля веса
function toggleWeightField() {
    const weightRadios = document.querySelectorAll('input[name="weight_type"]');
    const weightGroup = document.getElementById('weightGroup');
    
    if (!weightGroup) return;
    
    let showWeight = false;
    weightRadios.forEach(radio => {
        if (radio.checked && radio.value === 'weighted') {
            showWeight = true;
        }
    });
    
    weightGroup.style.display = showWeight ? 'block' : 'none';
}

// Функция для создания графика на дашборде
function createEffectivenessChart(data) {
    const canvas = document.getElementById('effectivenessChart');
    if (!canvas) return;
    
    // Здесь можно использовать Chart.js или другой графический библиотеку
    // Для простоты используем простую визуализацию
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = '#667eea';
    
    const maxValue = Math.max(...data, 1);
    const barWidth = (width - 100) / data.length;
    
    data.forEach((value, index) => {
        const barHeight = (value / maxValue) * (height - 50);
        const x = 50 + index * barWidth;
        const y = height - barHeight - 20;
        
        ctx.fillRect(x, y, barWidth - 5, barHeight);
        
        ctx.fillStyle = '#333';
        ctx.font = '10px Arial';
        ctx.fillText(value.toFixed(2), x, y - 5);
        ctx.fillStyle = '#667eea';
    });
}

// Автоматическое скрытие сообщений
function autoHideMessages() {
    const messages = document.querySelectorAll('.alert');
    messages.forEach(message => {
        if (!message.classList.contains('persistent')) {
            setTimeout(() => {
                message.style.opacity = '0';
                setTimeout(() => {
                    if (message.parentNode) {
                        message.remove();
                    }
                }, 300);
            }, 5000);
        }
    });
}

// Обработка отправки формы
function setupFormHandlers() {
    const form = document.querySelector('form');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        const formData = new FormData(form);
        if (!validateGraphForm(formData)) {
            e.preventDefault();
        }
    });
    
    // Обновление максимального количества связей при изменении параметров
    const numAgentsInput = document.getElementById('num_agents');
    const directedRadios = document.querySelectorAll('input[name="directed"]');
    
    if (numAgentsInput) {
        numAgentsInput.addEventListener('input', updateMaxEdges);
    }
    
    directedRadios.forEach(radio => {
        radio.addEventListener('change', updateMaxEdges);
    });
    
    // Обработка переключения типа весов
    const weightRadios = document.querySelectorAll('input[name="weight_type"]');
    weightRadios.forEach(radio => {
        radio.addEventListener('change', toggleWeightField);
    });
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    autoHideMessages();
    setupFormHandlers();
    updateMaxEdges();
    toggleWeightField();
    
    // Загрузка статистики для дашборда
    if (window.location.pathname === '/' || window.location.pathname === '/dashboard/') {
        loadDashboardStats();
    }
    
    // Добавление стилей для анимаций
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    `;
    document.head.appendChild(style);
});

// Экспорт функций для глобального использования
window.confirmDelete = confirmDelete;
window.exportData = exportData;
window.showNotification = showNotification;