from django.core.exceptions import ValidationError

def validate_graph_parameters(num_agents, num_edges, directed):
    errors = []
    if num_agents < 2:
        errors.append("Количество агентов должно быть не менее 2")
    if num_agents > 100:
        errors.append("Количество агентов не должно превышать 100")
    max_edges = num_agents * (num_agents - 1)
    if not directed:
        max_edges //= 2
    if num_edges < 1:
        errors.append("Количество связей должно быть не менее 1")
    if num_edges > max_edges:
        errors.append(f"Количество связей не может превышать {max_edges} для {num_agents} агентов")
    if errors:
        raise ValidationError(errors)
    return True