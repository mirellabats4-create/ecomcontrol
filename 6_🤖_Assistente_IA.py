import streamlit as st
from utils.helpers import (
    apply_custom_css, 
    get_sentiment_badge, 
    get_priority_badge
)
from services.ia_service import (
    gerar_resposta_atendimento,
    analisar_sentimento_urgencia,
    chat_assistente_ecommerce,
    melhorar_texto,
    is_api_configured
)
from database import get_clientes, get_pedidos

st.set_page_config(page_title="Assistente IA • EcomControl", page_icon="🤖", layout="wide")
apply_custom_css()

st.markdown("""
<div class="hero-container">
    <div class="hero-title">🤖 Assistente de Inteligência Artificial Google GenAI</div>
    <div class="hero-subtitle">Consultoria de operações de e-commerce, gerador de respostas para SAC, análise de sentimento e polimento de mensagens.</div>
</div>
""", unsafe_allow_html=True)

# Status da Conexão
if not is_api_configured():
    st.info("💡 **Dica:** O assistente está operando no modo demonstração. Para ativar o modelo Gemini 2.5 Flash ao vivo, configure a variável `GEMINI_API_KEY` no arquivo `.env` ou no menu lateral.")

tab_chat, tab_gerador, tab_analise, tab_polir = st.tabs([
    "💬 Chatbot Especialista", 
    "✍️ Gerador de Respostas SAC", 
    "🔍 Analisador de Sentimento", 
    "🪄 Polidor de Textos"
])

# ==========================================
# ABA 1: CHATBOT ESPECIALISTA EM E-COMMERCE
# ==========================================
with tab_chat:
    st.markdown("### 💬 **Consultor IA em E-commerce & Marketplaces**")
    st.caption("Tire dúvidas sobre mediações no Mercado Livre, Shopee, logística reversa, disputas de chargeback e CDC.")
    
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = [
            {"role": "assistant", "content": "Olá! Sou o assistente de IA do EcomControl. Como posso ajudar com a operação, atendimento ou logística da sua loja hoje?"}
        ]
    
    col_c1, col_c2 = st.columns([8, 2])
    with col_c2:
        if st.button("🗑️ Limpar Conversa", use_container_width=True):
            st.session_state["chat_history"] = [
                {"role": "assistant", "content": "Conversa reiniciada! Como posso te ajudar agora?"}
            ]
            st.rerun()
            
    # Renderiza o histórico de mensagens
    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Input de nova mensagem
    user_prompt = st.chat_input("Digite sua dúvida operacional ou peça um modelo de resposta...")
    if user_prompt:
        st.session_state["chat_history"].append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Pensando na melhor solução..."):
                resposta_ia = chat_assistente_ecommerce(st.session_state["chat_history"], user_prompt)
                st.markdown(resposta_ia)
                st.session_state["chat_history"].append({"role": "assistant", "content": resposta_ia})

# ==========================================
# ABA 2: GERADOR DE RESPOSTAS SAC
# ==========================================
with tab_gerador:
    st.markdown("### ✍️ **Gerador Instantâneo de Respostas para Clientes**")
    st.caption("Crie comunicações empáticas e profissionais personalizadas com os dados reais do pedido.")
    
    col_g1, col_g2 = st.columns([5, 5])
    
    with col_g1:
        st.markdown("#### 📋 Dados do Chamado")
        
        # Opção de carregar dados existentes do banco
        clientes = get_clientes()
        pedidos = get_pedidos()
        
        usar_dados_banco = st.checkbox("Carregar dados de um pedido existente no sistema", value=False)
        
        if usar_dados_banco and pedidos:
            ped_dict = {p["id"]: f"{p['codigo_pedido']} - {p['cliente_nome']} ({p['produto']})" for p in pedidos}
            sel_p_id = st.selectbox("Selecione o pedido:", options=list(ped_dict.keys()), format_func=lambda x: ped_dict[x])
            sel_ped_obj = next((p for p in pedidos if p["id"] == sel_p_id), None)
            
            nome_cli = sel_ped_obj["cliente_nome"] if sel_ped_obj else ""
            cod_ped = sel_ped_obj["codigo_pedido"] if sel_ped_obj else ""
            prod_desc = sel_ped_obj["produto"] if sel_ped_obj else ""
        else:
            nome_cli = st.text_input("Nome do Cliente:", placeholder="Ex: Carlos Eduardo")
            cod_ped = st.text_input("Código do Pedido:", placeholder="Ex: PED-2026-1003")
            prod_desc = st.text_input("Produto:", placeholder="Ex: Teclado Mecânico Gamer")
            
        motivo = st.selectbox("Motivo do Contato / Problema:", [
            "Atraso na Entrega / Rastreio parado",
            "Solicitação de Código de Rastreamento",
            "Produto com Defeito / Troca em Garantia",
            "Cancelamento e Solicitação de Estorno",
            "Item Incorreto ou Faltando",
            "Dúvida sobre Modo de Uso ou Instalação",
            "Agradecimento / Feedback Positivo"
        ])
        
        tom = st.selectbox("Tom da Mensagem:", [
            "Empático, Gentil e Resolutivo",
            "Formal e Institucional",
            "Rápido, Direto e Objetivo",
            "Firme e Focado em Termos & Prazos da Loja"
        ])
        
        msg_cliente = st.text_area("Mensagem enviada pelo Cliente:", placeholder="Cole aqui o texto exato que o cliente mandou...", height=100)
        contexto_extra = st.text_input("Instruções Adicionais para a IA (Opcional):", placeholder="Ex: Informar que enviamos brinde de desculpas")
        
        btn_gerar_sac = st.button("🚀 Gerar Resposta com Gemini IA", use_container_width=True, type="primary")

    with col_g2:
        st.markdown("#### 🤖 Resposta Gerada")
        if btn_gerar_sac:
            with st.spinner("Gerando resposta personalizada com Google GenAI..."):
                resposta_gerada = gerar_resposta_atendimento(
                    cliente_nome=nome_cli,
                    pedido_codigo=cod_ped,
                    produto=prod_desc,
                    mensagem_cliente=msg_cliente,
                    tom=tom,
                    motivo_problema=motivo,
                    contexto_extra=contexto_extra
                )
                st.session_state["sac_resposta_atual"] = resposta_gerada
        
        texto_sac = st.session_state.get("sac_resposta_atual", "")
        if texto_sac:
            st.markdown(f"""
            <div class="ai-response-box">
                {texto_sac.replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)
            st.text_area("Texto selecionável para copiar:", value=texto_sac, height=200)
        else:
            st.info("Preencha os dados ao lado e clique em **Gerar Resposta com Gemini IA** para visualizar a mensagem sugerida.")

# ==========================================
# ABA 3: ANALISADOR DE SENTIMENTO & URGÊNCIA
# ==========================================
with tab_analise:
    st.markdown("### 🔍 **Analisador de Sentimento, Gravidade & Urgência**")
    st.caption("Classifique mensagens recebidas para priorizar atendimentos críticos e evitar reclamações públicas.")
    
    col_a1, col_a2 = st.columns([5, 5])
    with col_a1:
        msg_analisar = st.text_area(
            "Cole a Mensagem do Cliente:",
            value="Comprei um teclado tem 10 dias e até agora nem enviaram o código de rastreio! Se não resolverem hoje vou abrir reclamação no Procon e cancelar no cartão!",
            height=150
        )
        btn_analisar = st.button("🔬 Analisar Mensagem com IA", use_container_width=True, type="primary")
        
    with col_a2:
        st.markdown("#### 📊 Diagnóstico Inteligente")
        if btn_analisar and msg_analisar:
            with st.spinner("Classificando sentimento e risco com Gemini..."):
                res_analise = analisar_sentimento_urgencia(msg_analisar)
                
                s_badge = get_sentiment_badge(res_analise.get("sentimento", "Neutro"))
                u_badge = get_priority_badge(res_analise.get("urgencia", "Média"))
                
                st.markdown(f"""
                <div class="metric-card">
                    <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
                        <div><strong>Sentimento:</strong> {s_badge}</div>
                        <div><strong>Urgência:</strong> {u_badge}</div>
                    </div>
                    <p><strong>📌 Resumo do Caso:</strong> {res_analise.get('resumo', '-')}</p>
                    <p><strong>🎯 Ação Recomendada:</strong> {res_analise.get('acao_recomendada', '-')}</p>
                    <p><strong>🏷️ Palavras-chave:</strong> {', '.join(res_analise.get('palavras_chave', []))}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Cole o texto da mensagem e clique em **Analisar Mensagem com IA**.")

# ==========================================
# ABA 4: POLIDOR & OTIMIZADOR DE TEXTOS
# ==========================================
with tab_polir:
    st.markdown("### 🪄 **Polidor e Revisor de Respostas de SAC**")
    st.caption("Transforme respostas informais, secas ou com erros em mensagens elegantes e persuasivas.")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        rascunho = st.text_area("Seu Rascunho / Texto Original:", placeholder="Ex: oi amigo ja mandamo seu pacote segue codigo de rastreio ai BR12345 vlw", height=150)
        objetivo_polir = st.selectbox("Estilo de Melhoria:", [
            "Mais Profissional, Cordial e Acolhedor",
            "Mais Curto e Conciso (WhatsApp)",
            "Mais Firme e Amparado nas Regras da Loja",
            "Empático para Acalmar Cliente Irritado"
        ])
        btn_polir = st.button("✨ Aprimorar Texto", use_container_width=True, type="primary")
        
    with col_p2:
        st.markdown("#### 🌟 Texto Aprimorado")
        if btn_polir and rascunho:
            with st.spinner("Reescrevendo e polindo mensagem..."):
                texto_melhorado = melhorar_texto(rascunho, objetivo=objetivo_polir)
                st.text_area("Resultado Pronto para Envio:", value=texto_melhorado, height=180)
        else:
            st.info("Digite um rascunho ao lado para gerar uma versão melhorada.")
