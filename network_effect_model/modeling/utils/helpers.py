def format_effect_value(value):
    """Форматирование значения эффекта"""
    if value is None:
        return "N/A"
    return f"{value:.4f}"

def calculate_percentage(part, whole):
    """Расчет процента"""
    if whole == 0:
        return 0
    return (part / whole) * 100

def get_effect_color(effect_value):
    """Получение цвета для значения эффекта"""
    if effect_value >= 70:
        return '#28a745'  # Зеленый
    elif effect_value >= 40:
        return '#ffc107'  # Желтый
    else:
        return '#dc3545'  # Красный