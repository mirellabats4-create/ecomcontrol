import os
import json
import re
from dotenv import load_dotenv
import streamlit as st

# Carrega variáveis de ambiente do .env
load_dotenv()

def get_api_key() -> str:
    """Recupera a chave de API do Gemini a partir do session_state ou variáveis de ambiente."""
    if hasattr(st, "session_state") and "GEMINI_API_KEY" in st.session_state and st.session_state["GEMINI_API_KEY"]:
        return st.session_state["GEMINI_API_KEY"].strip()
    return os.getenv("GEMINI_API_KEY", "").strip()

def is_api_configured() -> bool:
    """Verifica se a chave da API do Gemini está configurada."""
    key = get_api_key()
    return bool(key and key != "sua_chave_gemini_aqui" and len(key) > 10)

def get_gemini_client():
    """Inicializa e retorna o cliente oficial do Google GenAI."""
    key = get_api_key()
    if not key:
        return None
    try:
        from google import genai
        client = genai.Client(api_key=key)
        return client
    except ImportError:
        return None
    except Exception as e:
        st.error(f"Erro ao instanciar cliente Google GenAI: {str(e)}")
        return None

def gerar_resposta_atendimento(cliente_nome: str, pedido_codigo: str = None, produto: str = None, mensagem_cliente: str = "", tom: str = "Empático e Resolutivo", motivo_problema: str = None, contexto_extra: str = None) -> str:
    """
    Gera uma resposta profissional para SAC de e-commerce usando o Google GenAI.
    """
    client = get_gemini_client()
    
    # Prompt estruturado para o agente de SAC
    prompt = f"""Você é o especialista sênior de Atendimento e Sucesso do Cliente (SAC) da plataforma EcomControl.
Sua missão é responder à mensagem de um cliente com excelência, clareza, empatia e objetividade comercial.

DADOS DO ATENDIMENTO:
- Nome do Cliente: {cliente_nome or 'Cliente'}
- Código do Pedido: {pedido_codigo or 'Não informado'}
- Produto Relacionado: {produto or 'Não informado'}
- Motivo/Problema Relatado: {motivo_problema or 'Dúvida / Atendimento geral'}
- Mensagem enviada pelo Cliente: "{mensagem_cliente}"
- Tom desejado para a resposta: {tom}
{f'- Contexto / Instruções adicionais da equipe: {contexto_extra}' if contexto_extra else ''}

DIRETRIZES DA RESPOSTA:
1. Comece com uma saudação calorosa e personalizada usando o nome do cliente.
2. Demonstre empatia com a situação apresentada sem criar atritos.
3. Dê uma resposta prática e resolutiva (ou explique os próximos passos imediatos).
4. Utilize linguagem clara, sem jargões desnecessários, com pontuação impecável em Português do Brasil.
5. Finalize deixando o canal aberto para qualquer dúvida e com uma despedida cordial.
6. Retorne APENAS o texto final da mensagem pronta para ser enviada pelo operador humano.
"""

    if client:
        try:
            # Modelos recomendados: gemini-2.5-flash ou gemini-2.0-flash
            for model_name in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                    if response and response.text:
                        return response.text.strip()
                except Exception:
                    continue
        except Exception as e:
            st.warning(f"Aviso ao consultar Gemini: {str(e)}. Utilizando resposta simulada do assistente.")

    # Fallback inteligente e humanizado caso a API Key não esteja configurada ou ocorra erro de rede
    return f"""Olá, {cliente_nome or 'tudo bem'}!

Agradecemos pelo seu contato com a nossa equipe de suporte. 

Identificamos a sua solicitação referente ao pedido {pedido_codigo or 'informado'} ({produto or 'item'}). Compreendemos perfeitamente a importância dessa questão e já priorizamos seu atendimento interno.

Nossa equipe operacional está cuidando do caso com máxima atenção e te manteremos informado a cada atualização no status.

Caso precise de qualquer informação complementar, estamos à sua inteira disposição!

Atenciosamente,
Equipe de Atendimento EcomControl"""

def analisar_sentimento_urgencia(mensagem_cliente: str) -> dict:
    """
    Analisa o sentimento, urgência, pontos-chave e ação recomendada para a mensagem de um cliente.
    """
    default_result = {
        "sentimento": "Neutro",
        "urgencia": "Média",
        "resumo": "Solicitação padrão de suporte.",
        "acao_recomendada": "Responder ao cliente informando status atualizado.",
        "palavras_chave": ["suporte", "pedido"]
    }
    
    if not mensagem_cliente:
        return default_result

    client = get_gemini_client()
    if client:
        prompt = f"""Analise a seguinte mensagem enviada por um cliente de e-commerce e classifique rigorosamente seus parâmetros.

MENSAGEM:
"{mensagem_cliente}"

Retorne OBRIGATORIAMENTE APENAS um objeto JSON válido no seguinte formato:
{{
  "sentimento": "Positivo" | "Neutro" | "Negativo" | "Crítico",
  "urgencia": "Baixa" | "Média" | "Alta" | "Urgente",
  "resumo": "Breve resumo em 1 linha do que o cliente precisa",
  "acao_recomendada": "Ação operacional recomendada para o atendente",
  "palavras_chave": ["termo1", "termo2", "termo3"]
}}
"""
        try:
            for model_name in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                    if response and response.text:
                        clean_text = re.sub(r"```(?:json)?", "", response.text).strip()
                        data = json.loads(clean_text)
                        return data
                except Exception:
                    continue
        except Exception:
            pass

    # Heurística de fallback inteligente se a API estiver offline
    msg_low = mensagem_cliente.lower()
    if any(w in msg_low for w in ["procon", "processo", "advogado", "policia", "roubo", "fraude", "golpe", "absurdo"]):
        default_result["sentimento"] = "Crítico"
        default_result["urgencia"] = "Urgente"
        default_result["resumo"] = "Cliente extremamente insatisfeito relatando risco jurídico/grave."
        default_result["acao_recomendada"] = "Contato telefônico imediato da gerência de pós-venda."
    elif any(w in msg_low for w in ["atraso", "não chegou", "quebrado", "defeito", "errado", "danificado", "reembolso", "estorno", "cadê"]):
        default_result["sentimento"] = "Negativo"
        default_result["urgencia"] = "Alta"
        default_result["resumo"] = "Ocorrência operacional de entrega ou defeito."
        default_result["acao_recomendada"] = "Verificar transportadora e acionar garantia com prioridade."
    elif any(w in msg_low for w in ["obrigado", "parabéns", "excelente", "ótimo", "adorei", "perfeito", "chegou rápido"]):
        default_result["sentimento"] = "Positivo"
        default_result["urgencia"] = "Baixa"
        default_result["resumo"] = "Feedback positivo / elogio de compra."
        default_result["acao_recomendada"] = "Agradecer e convidar para avaliação na loja."
    
    return default_result

def chat_assistente_ecommerce(historico: list, mensagem_usuario: str) -> str:
    """
    Mantém uma conversa com o assistente inteligente especialista em e-commerce e SAC.
    """
    client = get_gemini_client()
    
    context_system = """Você é o EcomBot, o assistente de inteligência artificial do sistema EcomControl.
Você é um consultor e operador sênior especialista em:
- Operações de E-commerce, Logística e Logística Reversa (Correios, Jadlog, Loggi, etc.)
- Atendimento ao Cliente e Pós-Venda (SAC, Reclame Aqui, Procon, Direito do Consumidor CDC)
- Políticas dos principais Marketplaces brasileiros (Mercado Livre, Shopee, Amazon Brasil, Magalu)
- Resoluções de disputas, mediação de estornos, cancelamentos e prevenção de chargebacks.

Seja sempre prático, direto, profissional, prestativo e forneça exemplos práticos de mensagens prontas ou planos de ação passo a passo quando solicitado."""

    if client:
        try:
            # Constrói o histórico
            formatted_contents = [f"INSTRUÇÃO DO SISTEMA:\n{context_system}\n"]
            for msg in historico[-6:]:  # Últimas mensagens para manter contexto
                role_label = "Operador" if msg.get("role") == "user" else "Assistente EcomControl"
                formatted_contents.append(f"{role_label}: {msg.get('content')}")
            
            formatted_contents.append(f"Operador: {mensagem_usuario}")
            prompt_final = "\n\n".join(formatted_contents)

            for model_name in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt_final,
                    )
                    if response and response.text:
                        return response.text.strip()
                except Exception:
                    continue
        except Exception as e:
            st.warning(f"Aviso do assistente: {str(e)}")

    # Resposta inteligente offline
    return f"""Com base nas melhores práticas de e-commerce e atendimento:

1. **Diagnóstico da situação:** Para a questão informada ("{mensagem_usuario[:60]}..."), recomenda-se checar primeiro o código de rastreamento e o status no transportador.
2. **Abordagem com o cliente:** Mantenha postura empática, acolha a dúvida e fixe um prazo máximo de 24 horas para solução.
3. **Prevenção:** Caso seja um marketplace (ex: Mercado Livre/Shopee), responda antes de 12 horas para manter a métrica de reputação impecável.

*(Dica: Para habilitar as respostas dinâmicas avançadas do Gemini, certifique-se de configurar sua chave `GEMINI_API_KEY` na barra lateral ou no arquivo `.env`)*"""

def melhorar_texto(rascunho: str, objetivo: str = "Mais Profissional e Cordial") -> str:
    """Refina e aprimora um rascunho de texto escrito pelo atendente."""
    if not rascunho:
        return ""
        
    client = get_gemini_client()
    if client:
        prompt = f"""Você é um redator especialista em comunicação empresarial e suporte ao cliente.
Aprimore o rascunho de mensagem a seguir, mantendo a mensagem original e tornando-a {objetivo}.

RASCUNHO ORIGINAL:
"{rascunho}"

Retorne APENAS o texto aprimorado final pronto para envio:"""
        try:
            for model_name in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]:
                try:
                    res = client.models.generate_content(model=model_name, contents=prompt)
                    if res and res.text:
                        return res.text.strip()
                except Exception:
                    continue
        except Exception:
            pass
            
    return rascunho.strip()
