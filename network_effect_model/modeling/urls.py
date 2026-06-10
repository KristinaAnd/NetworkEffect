from django.urls import path
from . import views

app_name = 'modeling'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('generate/', views.generate_form, name='generate_form'),
    path('generate/submit/', views.generate_submit, name='generate_submit'),
    path('results/', views.list_results, name='list_results'),
    path('result/<int:pk>/', views.view_result, name='view_result'),
    path('result/<int:pk>/delete/', views.delete_result, name='delete_result'),
    
    # Экспорт
    path('export/<int:pk>/json/', views.export_json, name='export_json'),
    path('export/<int:pk>/csv/', views.export_csv, name='export_csv'),
    path('export/<int:pk>/excel/', views.export_excel, name='export_excel'),
    path('export/<int:pk>/pdf/', views.export_pdf, name='export_pdf'),
    
    # Экспорт дашборда
    path('export/dashboard/json/', views.export_dashboard_json, name='export_dashboard_json'),
    path('export/dashboard/csv/', views.export_dashboard_csv, name='export_dashboard_csv'),
    path('export/dashboard/excel/', views.export_dashboard_excel, name='export_dashboard_excel'),
    path('export/dashboard/pdf/', views.export_dashboard_pdf, name='export_dashboard_pdf'),
]