from django.contrib import admin
from .models import GraphModel

@admin.register(GraphModel)
class GraphModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'num_agents', 'num_edges', 'directed', 'weight_type', 'total_effect', 'business_value', 'created_at']
    list_filter = ['directed', 'weight_type', 'created_at']
    search_fields = ['name', 'id']
    readonly_fields = ['graph_data', 'structural_effect', 'functional_effect', 'total_effect', 'efficiency', 'business_value', 'risk_score', 'recommendation']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'num_agents', 'num_edges', 'directed', 'weight_type', 'weight_min', 'weight_max')
        }),
        ('Результаты моделирования', {
            'fields': ('structural_effect', 'functional_effect', 'total_effect', 'efficiency')
        }),
        ('Бизнес-метрики', {
            'fields': ('business_value', 'risk_score', 'recommendation')
        }),
        ('Данные', {
            'fields': ('graph_data',),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.name:
            obj.name = f"Модель от {obj.created_at.strftime('%d.%m.%Y %H:%M') if obj.created_at else 'сейчас'}"
        super().save_model(request, obj, form, change)