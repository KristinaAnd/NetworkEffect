from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class GraphModel(models.Model):
    """
    Модель для хранения результатов моделирования сетевого эффекта.
    Все расчёты основаны на формулах документа "ТРЕБОВАНИЯ.docx".
    """
    DIRECTED_CHOICES = [
        ('undirected', 'Ненаправленный'),
        ('directed', 'Направленный'),
    ]
    WEIGHT_TYPE_CHOICES = [
        ('unweighted', 'Без весов (все веса = 1)'),
        ('weighted', 'Взвешенный (случайные веса)'),
    ]
    BALANCE_CHOICES = [
        ('balanced', 'Симметричный (для направленного графа)'),
        ('unbalanced', 'Несимметричный'),
    ]

    name = models.CharField(max_length=200, blank=True, null=True)
    num_agents = models.IntegerField(default=10, validators=[MinValueValidator(2), MaxValueValidator(100)])
    num_edges = models.IntegerField(default=10, validators=[MinValueValidator(1)], verbose_name='Количество связей')
    directed = models.CharField(max_length=20, choices=DIRECTED_CHOICES, default='undirected')
    weight_type = models.CharField(max_length=20, choices=WEIGHT_TYPE_CHOICES, default='unweighted')
    # Параметр balance_type: для направленного графа – добавлять ли обратные рёбра (симметрия)
    balance_type = models.CharField(max_length=20, choices=BALANCE_CHOICES, default='balanced')
    weight_min = models.FloatField(default=0.1, null=True, blank=True)
    weight_max = models.FloatField(default=1.0, null=True, blank=True)
    weight_avg = models.FloatField(null=True, blank=True, verbose_name='Средний вес связи')

    graph_data = models.JSONField(null=True, blank=True)
    structural_effect = models.FloatField(null=True, blank=True)
    functional_effect = models.FloatField(null=True, blank=True)
    total_effect = models.FloatField(null=True, blank=True)
    efficiency = models.FloatField(null=True, blank=True, verbose_name='Эффективность цепочки поставок')

    business_value = models.FloatField(null=True, blank=True)
    risk_score = models.FloatField(null=True, blank=True)
    synergy_factor = models.FloatField(null=True, blank=True)
    economic_impact = models.FloatField(null=True, blank=True)
    recommendation = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Модель сетевого эффекта'
        verbose_name_plural = 'Модели сетевых эффектов'
        ordering = ['-created_at']

    def __str__(self):
        return f"Модель #{self.id} | TNE = {self.total_effect or 0:.4f}"

    def get_density(self):
        """
        Плотность D по формуле (4) документа:
        D = 2|E|/(N(N-1)) для ненаправленного,
        D = |E|/(N(N-1)) для направленного.
        """
        N = self.num_agents
        if N <= 1:
            return 0.0
        if self.directed == 'directed':
            max_edges = N * (N - 1)
            return self.num_edges / max_edges if max_edges > 0 else 0.0
        else:
            max_edges = N * (N - 1) // 2
            return (2 * self.num_edges) / max_edges if max_edges > 0 else 0.0