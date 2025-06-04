from .config_utils import load_config


def config_processor(request):
    """Agrega configuraciones de la clínica al contexto de las plantillas."""
    return {'config': load_config()}
