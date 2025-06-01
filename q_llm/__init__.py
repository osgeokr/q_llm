from .q_llm import QLLM

def classFactory(iface):
    # This function is required by QGIS to load the plugin
    return QLLM(iface)
