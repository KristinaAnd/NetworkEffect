import json
import csv
import pandas as pd
from io import StringIO, BytesIO
from django.http import HttpResponse
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
import base64

class ExportService:
    
    @staticmethod
    def export_to_json(graph_model, analysis_results):
        data = {
            'metadata': {
                'export_date': datetime.now().isoformat(),
                'graph_id': graph_model.id,
                'num_agents': graph_model.num_agents,
                'density_edges': graph_model.num_edges,
                'directed': graph_model.directed,
                'weighted': graph_model.weight_type == 'weighted'
            },
            'network_effects': {
                'structural': graph_model.structural_network_effect,
                'functional': graph_model.functional_network_effect,
                'total': graph_model.total_network_effect,
                'supply_chain_efficiency': graph_model.supply_chain_efficiency
            },
            'graph_data': graph_model.graph_data,
            'analysis': analysis_results
        }
        response = HttpResponse(json.dumps(data, indent=2, ensure_ascii=False), content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="network_effect_{graph_model.id}.json"'
        return response
    
    @staticmethod
    def export_to_csv(graph_model):
        output = StringIO()
        writer = csv.writer(output, delimiter=';')
        writer.writerow([
            'ID графа', 'Дата', 'Количество агентов', 'Количество связей',
            'Направленность', 'Тип весов', 'Структурный эффект',
            'Функциональный эффект', 'Общий эффект', 'Эффективность цепочки'
        ])
        structural = f"{graph_model.structural_network_effect:.4f}" if graph_model.structural_network_effect is not None else 'N/A'
        functional = f"{graph_model.functional_network_effect:.4f}" if graph_model.functional_network_effect is not None else 'N/A'
        total = f"{graph_model.total_network_effect:.4f}" if graph_model.total_network_effect is not None else 'N/A'
        efficiency = f"{graph_model.supply_chain_efficiency:.4f}" if graph_model.supply_chain_efficiency is not None else 'N/A'
        writer.writerow([
            graph_model.id,
            graph_model.created_at.strftime('%d.%m.%Y %H:%M'),
            graph_model.num_agents,
            graph_model.num_edges,
            graph_model.get_directed_display(),
            graph_model.get_weight_type_display(),
            structural,
            functional,
            total,
            efficiency
        ])
        response = HttpResponse(output.getvalue().encode('utf-8-sig'), content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="network_effect_{graph_model.id}.csv"'
        return response
    
    @staticmethod
    def export_to_excel(graph_model, analysis_results, G):
        output = BytesIO()
        structural = graph_model.structural_network_effect if graph_model.structural_network_effect is not None else 'N/A'
        functional = graph_model.functional_network_effect if graph_model.functional_network_effect is not None else 'N/A'
        total = graph_model.total_network_effect if graph_model.total_network_effect is not None else 'N/A'
        efficiency = graph_model.supply_chain_efficiency if graph_model.supply_chain_efficiency is not None else 'N/A'
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            metadata_df = pd.DataFrame([
                ['ID графа', graph_model.id],
                ['Дата создания', graph_model.created_at.strftime('%d.%m.%Y %H:%M:%S')],
                ['Количество агентов', graph_model.num_agents],
                ['Количество связей', graph_model.num_edges],
                ['Направленность', graph_model.get_directed_display()],
                ['Тип весов', graph_model.get_weight_type_display()],
                ['Мин. вес', graph_model.weight_min if graph_model.weight_min else 'N/A'],
                ['Макс. вес', graph_model.weight_max if graph_model.weight_max else 'N/A'],
                ['Структурный эффект', structural],
                ['Функциональный эффект', functional],
                ['Общий эффект', total],
                ['Эффективность цепочки', efficiency]
            ])
            metadata_df.to_excel(writer, sheet_name='Метаданные', index=False, header=False)
            if graph_model.graph_data:
                edges_data = []
                for edge in graph_model.graph_data.get('edges', []):
                    edges_data.append({
                        'Источник': edge['source'],
                        'Цель': edge['target'],
                        'Вес': edge.get('weight', 1)
                    })
                edges_df = pd.DataFrame(edges_data)
                edges_df.to_excel(writer, sheet_name='Связи', index=False)
        output.seek(0)
        response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="network_effect_{graph_model.id}.xlsx"'
        return response
    
    @staticmethod
    def generate_graph_image_base64(G, directed, weighted, balanced=False):
        """Генерация изображения графа в base64 для PDF с учётом сбалансированности"""
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(G, k=2, iterations=50)
        node_colors = ['#2E86AB' for _ in G.nodes()]
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=400, alpha=0.9)
        nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold')
        
        if directed:
            if balanced:
                for u, v, data in G.edges(data=True):
                    width = data.get('weight', 1) * 1.5 if weighted else 1.0
                    nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], arrowstyle='->', arrowsize=12,
                                           width=width, alpha=0.7, edge_color='#A23B72',
                                           connectionstyle="arc3,rad=0.1")
                    if G.has_edge(v, u) or balanced:
                        nx.draw_networkx_edges(G, pos, edgelist=[(v, u)], arrowstyle='->', arrowsize=12,
                                               width=width, alpha=0.7, edge_color='#A23B72',
                                               connectionstyle="arc3,rad=-0.1")
            else:
                for u, v, data in G.edges(data=True):
                    width = data.get('weight', 1) * 1.5 if weighted else 1.0
                    nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], arrowstyle='->', arrowsize=12,
                                           width=width, alpha=0.7, edge_color='#A23B72',
                                           connectionstyle="arc3,rad=0.1")
        else:
            if weighted:
                weights = [data.get('weight', 1) * 1.5 for _, _, data in G.edges(data=True)]
            else:
                weights = [1.0 for _ in G.edges()]
            nx.draw_networkx_edges(G, pos, width=weights, edge_color='#A23B72', alpha=0.7)
        
        title = f"{'Ориентированный' if directed else 'Неориентированный'} граф"
        if weighted:
            title += " (взвешенный)"
        if balanced and directed:
            title += " (сбалансированный)"
        plt.title(title, fontsize=12, fontweight='bold')
        plt.axis('off')
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        return image_base64
    
    @staticmethod
    def export_to_pdf(graph_model, analysis_results, G):
        graph_image_base64 = ExportService.generate_graph_image_base64(
            G,
            graph_model.directed == 'directed',
            graph_model.weight_type == 'weighted',
            graph_model.balance_type == 'balanced'
        )
        structural_value = f"{graph_model.structural_network_effect:.4f}" if graph_model.structural_network_effect is not None else 'N/A'
        functional_value = f"{graph_model.functional_network_effect:.4f}" if graph_model.functional_network_effect is not None else 'N/A'
        total_value = f"{graph_model.total_network_effect:.4f}" if graph_model.total_network_effect is not None else 'N/A'
        efficiency_value = f"{graph_model.supply_chain_efficiency:.4f}" if graph_model.supply_chain_efficiency is not None else 'N/A'
        weight_info = ""
        if graph_model.weight_type == 'weighted':
            weight_info = f"Мин. вес: {graph_model.weight_min}, Макс. вес: {graph_model.weight_max}"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Бизнес-отчет: Моделирование сетевых эффектов</title>
            <style>
                @page {{ size: A4; margin: 2cm; }}
                body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; color: #333; line-height: 1.6; }}
                .header {{ text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 3px solid #2E86AB; }}
                .header h1 {{ color: #2E86AB; margin: 0; font-size: 24px; }}
                .header h2 {{ color: #666; font-size: 14px; font-weight: normal; margin: 10px 0 0 0; }}
                .company-info {{ text-align: right; font-size: 10px; color: #999; margin-bottom: 20px; }}
                .section {{ margin-bottom: 30px; page-break-inside: avoid; }}
                .section-title {{ color: #2E86AB; border-left: 4px solid #A23B72; padding-left: 15px; margin-bottom: 15px; font-size: 18px; }}
                .metrics-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin: 20px 0; }}
                .metric-card {{ background: #f8f9fa; border-radius: 8px; padding: 15px; text-align: center; border: 1px solid #e0e0e0; }}
                .metric-card .value {{ font-size: 28px; font-weight: bold; color: #2E86AB; }}
                .metric-card .label {{ font-size: 12px; color: #666; margin-top: 5px; }}
                .stats-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                .stats-table td {{ padding: 10px; border-bottom: 1px solid #e0e0e0; }}
                .stats-table td:first-child {{ font-weight: bold; width: 40%; background: #f8f9fa; }}
                .graph-container {{ text-align: center; margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; }}
                .graph-container img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; }}
                .interpretation {{ background: #e8f4f8; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2E86AB; }}
                .footer {{ text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #e0e0e0; font-size: 10px; color: #999; }}
            </style>
        </head>
        <body>
            <div class="company-info"><strong>ООО «Нетворк Эффект»</strong><br>Система моделирования сетевых эффектов<br>Версия 2.0</div>
            <div class="header"><h1>Аналитический отчет</h1><h2>Моделирование сетевого эффекта в организационно-замкнутой экономической системе</h2></div>
            <div class="section"><div class="section-title">1. Параметры моделирования</div>
                <table class="stats-table">
                    <tr><td>Номер модели</td><td>#{graph_model.id}</td></tr>
                    <tr><td>Дата и время</td><td>{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</td></tr>
                    <tr><td>Количество агентов</td><td>{graph_model.num_agents}</td></tr>
                    <tr><td>Количество связей</td><td>{graph_model.num_edges}</td></tr>
                    <tr><td>Тип графа</td><td>{graph_model.get_directed_display()}</td></tr>
                    <tr><td>Тип весов</td><td>{graph_model.get_weight_type_display()}</td></tr>
                    <tr><td>Диапазон весов</td><td>{weight_info if weight_info else 'Не применяется'}</td></tr>
                </table>
            </div>
            <div class="section"><div class="section-title">2. Результаты моделирования</div>
                <div class="metrics-grid">
                    <div class="metric-card"><div class="value">{structural_value}</div><div class="label">Структурный эффект</div></div>
                    <div class="metric-card"><div class="value">{functional_value}</div><div class="label">Функциональный эффект</div></div>
                    <div class="metric-card"><div class="value">{total_value}</div><div class="label">Общий сетевой эффект</div></div>
                    <div class="metric-card"><div class="value">{efficiency_value}</div><div class="label">Эффективность цепочки поставок</div></div>
                </div>
            </div>
            <div class="section"><div class="section-title">3. Визуализация сетевой структуры</div>
                <div class="graph-container"><img src="data:image/png;base64,{graph_image_base64}" alt="Граф сети"></div>
            </div>
            <div class="section"><div class="section-title">4. Бизнес-интерпретация</div>
                <div class="interpretation"><strong>Общий сетевой эффект: {total_value}</strong><br><br>{analysis_results.get('business_interpretation', 'Анализ завершен')}</div>
            </div>
            <div class="footer"><p>© 2024 ООО «Нетворк Эффект». Все права защищены.</p><p>Данный отчет является конфиденциальным и предназначен для внутреннего использования.</p></div>
        </body>
        </html>
        """
        response = HttpResponse(html_content, content_type='text/html')
        response['Content-Disposition'] = f'attachment; filename="business_report_{graph_model.id}.html"'
        return response