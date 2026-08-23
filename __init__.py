# Módulo de serviços de IA do EcomControl
from .ia_service import (
    gerar_resposta_atendimento,
    analisar_sentimento_urgencia,
    chat_assistente_ecommerce,
    melhorar_texto,
    is_api_configured,
    get_gemini_client
)

__all__ = [
    "gerar_resposta_atendimento",
    "analisar_sentimento_urgencia",
    "chat_assistente_ecommerce",
    "melhorar_texto",
    "is_api_configured",
    "get_gemini_client"
]
