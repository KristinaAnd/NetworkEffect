import networkx as nx
from typing import Dict, Any, Tuple

class NetworkEffectCalculator:
    def __init__(self, G: nx.Graph, directed: bool, weighted: bool):
        self.G = G
        self.directed = directed
        self.weighted = weighted
        self.num_agents = len(G)

    def calculate_structural_effect(self) -> float:
        N = self.num_agents
        actual_edges = self.G.number_of_edges()
        if self.directed:
            max_edges = N * (N - 1)
            D = actual_edges / max_edges if max_edges > 0 else 0
        else:
            max_edges = N * (N - 1) // 2
            D = (2 * actual_edges) / max_edges if max_edges > 0 else 0

        if self.directed:
            deg_sum = 2 * actual_edges
            deg_sq_sum = sum((self.G.in_degree(v) + self.G.out_degree(v)) ** 2 for v in self.G.nodes())
        else:
            deg_sum = 2 * actual_edges
            deg_sq_sum = sum(d ** 2 for d in dict(self.G.degree()).values())

        if N > 0 and deg_sq_sum > 0:
            B = (deg_sum ** 2) / (N * deg_sq_sum)
        else:
            B = 0

        return round(N * D * B, 4)

    def calculate_functional_effect(self) -> float:
        actual_edges = self.G.number_of_edges()
        if self.weighted:
            total_weight = sum(data.get('weight', 1) for _, _, data in self.G.edges(data=True))
        else:
            total_weight = actual_edges
        return round(total_weight, 4)

    def calculate_total_effect(self) -> Tuple[float, Dict[str, Any]]:
        structural = self.calculate_structural_effect()
        functional = self.calculate_functional_effect()
        total = (structural * functional) ** 0.5 if structural > 0 and functional > 0 else 0
        details = {
            'structural_effect': structural,
            'functional_effect': functional,
            'total_effect': round(total, 4),
            'synergy_score': round(structural * functional, 4),
            'business_interpretation': self._get_business_interpretation(total)
        }
        return total, details

    def _get_business_interpretation(self, effect: float) -> str:
        if effect >= 70:
            return "Высокий уровень сетевого взаимодействия. Система работает эффективно."
        elif effect >= 50:
            return "Средний уровень. Требуется оптимизация ключевых связей."
        elif effect >= 30:
            return "Низкий уровень. Рекомендуется реорганизация структуры."
        else:
            return "Критический уровень. Необходимо кардинальное изменение архитектуры сети."

    def get_effectiveness_grade(self, effect: float) -> str:
        if effect >= 80:
            return "A (Отлично)"
        elif effect >= 60:
            return "B (Хорошо)"
        elif effect >= 40:
            return "C (Удовлетворительно)"
        elif effect >= 20:
            return "D (Плохо)"
        else:
            return "F (Критически)"