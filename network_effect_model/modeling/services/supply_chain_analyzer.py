import networkx as nx
import numpy as np
from typing import Dict, Any, List, Tuple
from collections import defaultdict

class SupplyChainAnalyzer:
    """Анализатор цепочек поставок"""
    
    def __init__(self, G: nx.Graph, directed: bool, weighted: bool):
        self.G = G
        self.directed = directed
        self.weighted = weighted
        
    def analyze_efficiency(self) -> Dict[str, Any]:
        results = {
            'efficiency_score': 0.0,
            'bottlenecks': [],
            'critical_nodes': [],
            'optimization_suggestions': []
        }
        bottlenecks = self._find_bottlenecks()
        results['bottlenecks'] = bottlenecks
        results['critical_nodes'] = self._find_critical_nodes()
        results['throughput'] = self._calculate_throughput()
        results['resilience'] = self._calculate_resilience()
        results['redundancy'] = self._calculate_redundancy()
        results['efficiency_score'] = self._calculate_overall_efficiency(results)
        results['optimization_suggestions'] = self._generate_recommendations(results)
        return results
    
    def _find_bottlenecks(self) -> List[Dict[str, Any]]:
        bottlenecks = []
        try:
            betweenness = nx.betweenness_centrality(self.G)
        except:
            betweenness = {node: 0 for node in self.G.nodes()}
        for node in self.G.nodes():
            degree = self.G.degree(node)
            betw = betweenness.get(node, 0)
            if betw > 0.3 and degree < 2:
                bottlenecks.append({
                    'node': node,
                    'degree': degree,
                    'betweenness': betw,
                    'impact': 'Высокий',
                    'description': f'Узел {node} является критическим для передачи информации'
                })
        return bottlenecks
    
    def _find_critical_nodes(self) -> List[int]:
        try:
            if self.directed:
                centrality = nx.eigenvector_centrality_numpy(self.G.to_undirected())
            else:
                centrality = nx.eigenvector_centrality_numpy(self.G)
            threshold = np.percentile(list(centrality.values()), 80) if centrality.values() else 0
            critical = [node for node, cent in centrality.items() if cent >= threshold]
            return critical
        except:
            return []
    
    def _calculate_throughput(self) -> float:
        if self.G.number_of_edges() == 0:
            return 0.0
        avg_degree = 2 * self.G.number_of_edges() / self.G.number_of_nodes() if self.G.number_of_nodes() > 0 else 0
        max_degree = max(dict(self.G.degree()).values()) if self.G.degree() else 0
        throughput = avg_degree / max_degree if max_degree > 0 else 0
        return throughput
    
    def _calculate_resilience(self) -> float:
        if self.G.number_of_nodes() <= 1:
            return 0.0
        try:
            if self.directed:
                G_undirected = self.G.to_undirected()
                connectivity = nx.node_connectivity(G_undirected)
            else:
                connectivity = nx.node_connectivity(self.G)
            resilience = connectivity / self.G.number_of_nodes() if self.G.number_of_nodes() > 0 else 0
            return resilience
        except:
            return 0.0
    
    def _calculate_redundancy(self) -> float:
        if self.G.number_of_edges() == 0:
            return 0.0
        try:
            total_alternatives = 0
            node_pairs = 0
            if self.directed:
                nodes = list(self.G.nodes())
                for i in range(len(nodes)):
                    for j in range(len(nodes)):
                        if i != j:
                            try:
                                paths = list(nx.all_simple_paths(self.G, nodes[i], nodes[j], cutoff=3))
                                total_alternatives += len(paths) - 1 if len(paths) > 1 else 0
                                node_pairs += 1
                            except:
                                continue
            else:
                nodes = list(self.G.nodes())
                for i in range(len(nodes)):
                    for j in range(i + 1, len(nodes)):
                        try:
                            paths = list(nx.all_simple_paths(self.G, nodes[i], nodes[j], cutoff=3))
                            total_alternatives += len(paths) - 1 if len(paths) > 1 else 0
                            node_pairs += 1
                        except:
                            continue
            redundancy = total_alternatives / node_pairs if node_pairs > 0 else 0
            return min(redundancy / 3, 1.0)
        except:
            return 0.0
    
    def _calculate_overall_efficiency(self, metrics: Dict[str, Any]) -> float:
        weights = {'throughput': 0.3, 'resilience': 0.4, 'redundancy': 0.3}
        efficiency = (metrics.get('throughput', 0) * weights['throughput'] +
                      metrics.get('resilience', 0) * weights['resilience'] +
                      metrics.get('redundancy', 0) * weights['redundancy'])
        return efficiency
    
    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        recommendations = []
        if metrics.get('throughput', 0) < 0.3:
            recommendations.append("Рекомендуется увеличить количество связей для улучшения пропускной способности")
        if metrics.get('resilience', 0) < 0.2:
            recommendations.append("Низкая устойчивость сети. Добавьте резервные связи между ключевыми узлами")
        if metrics.get('redundancy', 0) < 0.2:
            recommendations.append("Недостаточно альтернативных маршрутов. Рассмотрите возможность создания дублирующих связей")
        if metrics.get('bottlenecks'):
            recommendations.append("Обнаружены узкие места. Рекомендуется усилить эти позиции")
        if not recommendations:
            recommendations.append("Сеть хорошо сбалансирована. Продолжайте мониторинг показателей")
        return recommendations