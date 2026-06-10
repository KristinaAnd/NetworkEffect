import networkx as nx
import random

class GraphGenerator:
    def __init__(self, num_agents, num_edges, directed, weighted, balanced, weight_min, weight_max):
        self.num_agents = num_agents
        self.num_edges = num_edges
        self.directed = directed
        self.weighted = weighted
        self.balanced = balanced
        self.weight_min = weight_min
        self.weight_max = weight_max

    def generate(self):
        if self.directed:
            G = nx.DiGraph()
        else:
            G = nx.Graph()
        G.add_nodes_from(range(self.num_agents))

        max_possible = self.num_agents * (self.num_agents - 1)
        if not self.directed:
            max_possible //= 2

        target = min(self.num_edges, max_possible)

        if self.directed and self.balanced:
            if target % 2 != 0:
                target -= 1
                if target < 0:
                    target = 0

        edges_added = 0
        attempts = 0
        max_attempts = target * 10
        existing = set()

        while edges_added < target and attempts < max_attempts:
            u = random.randint(0, self.num_agents - 1)
            v = random.randint(0, self.num_agents - 1)
            if u == v:
                attempts += 1
                continue
            if not self.directed and u > v:
                u, v = v, u
            edge = (u, v)
            if edge in existing:
                attempts += 1
                continue

            if self.weighted:
                w = round(random.uniform(self.weight_min, self.weight_max), 3)
                G.add_edge(u, v, weight=w)
            else:
                G.add_edge(u, v)

            existing.add(edge)
            edges_added += 1

            if self.directed and self.balanced:
                rev = (v, u)
                if rev not in existing:
                    if self.weighted:
                        G.add_edge(v, u, weight=w)
                    else:
                        G.add_edge(v, u)
                    existing.add(rev)
                    edges_added += 1

            attempts += 1

        return G

    def generate_random(self):
        return self.generate()

    def calculate_effects(self, G):
        N = self.num_agents
        actual_edges = G.number_of_edges()

        if self.directed:
            max_edges = N * (N - 1)
            D = actual_edges / max_edges if max_edges > 0 else 0
        else:
            max_edges = N * (N - 1) // 2
            D = (2 * actual_edges) / max_edges if max_edges > 0 else 0

        if self.directed:
            deg_sum = 2 * actual_edges
            deg_sq_sum = sum((G.in_degree(v) + G.out_degree(v)) ** 2 for v in G.nodes())
        else:
            deg_sum = 2 * actual_edges
            deg_sq_sum = sum(d ** 2 for d in dict(G.degree()).values())

        if N > 0 and deg_sq_sum > 0:
            B = (deg_sum ** 2) / (N * deg_sq_sum)
        else:
            B = 0.0

        structural = N * D * B

        if self.weighted:
            total_weight = sum(data.get('weight', 1) for _, _, data in G.edges(data=True))
        else:
            total_weight = actual_edges
        functional = total_weight

        if structural > 0 and functional > 0:
            total = (structural * functional) ** 0.5
        else:
            total = 0.0

        return round(structural, 4), round(functional, 4), round(total, 4), round(B, 4)

    def get_stats(self, G):
        N = self.num_agents
        actual_edges = G.number_of_edges()
        if self.directed:
            max_edges = N * (N - 1)
            density_percent = (actual_edges / max_edges * 100) if max_edges > 0 else 0
        else:
            max_edges = N * (N - 1) // 2
            density_percent = (2 * actual_edges / max_edges * 100) if max_edges > 0 else 0
        
        stats = {
            'nodes': G.number_of_nodes(),
            'edges': actual_edges,
            'density_percent': round(density_percent, 1),
            'is_directed': self.directed,
            'is_weighted': self.weighted,
            'is_balanced': self.balanced,
        }
        if self.weighted and actual_edges > 0:
            weights = [d.get('weight', 1) for _, _, d in G.edges(data=True)]
            stats['weight_min'] = min(weights)
            stats['weight_max'] = max(weights)
            stats['weight_avg'] = round(sum(weights) / len(weights), 3)
        else:
            stats['weight_avg'] = 1.0
        return stats