import streamlit as st
import pandas as pd
from database import init_db, get_kpis, get_pedidos, get_atendimentos, get_problemas
from utils.helpers import (
    apply_custom_css, 
    format_currency, 
    format_date, 
    get_status_badge, 
    get_priority_badge,
    get_sentiment_badge
)
from services.ia_service import is_api_configured

# 1. Configuração Global da Página
st.set_page_config(
    page_title="EcomControl - Central de Gestão & Suporte",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inicialização do Banco de Dados
init_db()

# 3. Aplicação do CSS Personalizado
apply_custom_css()

# 4. Barra Lateral (Sidebar)
with st.sidebar:
    st.markdown("## ⚡ **EcomControl**")
    st.caption("Sistema Integrado de Gestão, Pós-Venda & IA para E-commerce")
    st.divider()
    
    # Status da IA (Google GenAI)
    st.markdown("### 🤖 **Status do Google GenAI**")
    api_ready = is_api_configured()
    if api_ready:
        st.success("🟢 API Gemini Conectada")
    else:
        st.warning("🟡 Modo Demonstração (Sem Chave)")
        with st.expander("🔑 Configurar API Key"):
            st.markdown("Insira sua **Gemini API Key** abaixo para ativar respostas em tempo real:")
            user_key = st.text_input("Gemini API Key:", type="password", key="gemini_key_input", placeholder="AIzaSy...")
            if user_key:
                st.session_state["GEMINI_API_KEY"] = user_key.strip()
                st.rerun()
            st.caption("Ou defina `GEMINI_API_KEY` no arquivo `.env`.")

    st.divider()
    
    # Resumo Rápido do Sistema
    kpis = get_kpis()
    st.markdown("### 📊 **Visão Geral**")
    st.markdown(f"👥 **Clientes:** `{kpis['total_clientes']}`")
    st.markdown(f"📦 **Pedidos:** `{kpis['total_pedidos']}`")
    st.markdown(f"⚠️ **Problemas Abertos:** `{kpis['problemas_abertos']}`")
    st.markdown(f"💬 **SAC Pendente:** `{kpis['atendimentos_pendentes']}`")
    
    st.divider()
    st.caption("© 2026 EcomControl • v1.0.0")

# 5. Banner Hero Principal
st.markdown("""
<div class="hero-container">
    <div class="hero-title">⚡ EcomControl • Central de Operações & Pós-Venda</div>
    <div class="hero-subtitle">Plataforma unificada para controle de pedidos, resolução ágil de problemas de clientes e suporte assistido por Inteligência Artificial.</div>
</div>
""", unsafe_allow_html=True)

# 6. Indicadores Chave de Desempenho (KPI Cards)
kpis = get_kpis()

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <span style="color:#64748B; font-size:13px; font-weight:600;">FATURAMENTO TOTAL</span>
        <div style="font-size:22px; font-weight:700; color:#0F172A; margin-top:5px;">{format_currency(kpis['faturamento_total'])}</div>
        <span style="color:#10B981; font-size:12px; font-weight:600;">Ticket Médio: {format_currency(kpis['ticket_medio'])}</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <span style="color:#64748B; font-size:13px; font-weight:600;">TOTAL DE PEDIDOS</span>
        <div style="font-size:22px; font-weight:700; color:#0F172A; margin-top:5px;">{kpis['total_pedidos']}</div>
        <span style="color:#3B82F6; font-size:12px; font-weight:600;">{kpis['pedidos_entregues']} Entregues</span>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <span style="color:#64748B; font-size:13px; font-weight:600;">PROBLEMAS ABERTOS</span>
        <div style="font-size:22px; font-weight:700; color:#EF4444; margin-top:5px;">{kpis['problemas_abertos']}</div>
        <span style="color:#EF4444; font-size:12px; font-weight:600;">{kpis['problemas_urgentes']} Urgentes</span>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <span style="color:#64748B; font-size:13px; font-weight:600;">SAC / ATENDIMENTOS</span>
        <div style="font-size:22px; font-weight:700; color:#F59E0B; margin-top:5px;">{kpis['atendimentos_pendentes']}</div>
        <span style="color:#F59E0B; font-size:12px; font-weight:600;">Aguardando resposta</span>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card">
        <span style="color:#64748B; font-size:13px; font-weight:600;">TAXA DE RESOLUÇÃO</span>
        <div style="font-size:22px; font-weight:700; color:#10B981; margin-top:5px;">{kpis['taxa_resolucao']}%</div>
        <span style="color:#10B981; font-size:12px; font-weight:600;">Eficiência Operacional</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 7. Módulos do Sistema (Cards Navegacionais)
st.markdown("### 🗂️ **Módulos do Sistema**")
mcol1, mcol2, mcol3, mcol4 = st.columns(4)

with mcol1:
    st.markdown("""
    <div class="metric-card" style="min-height: 150px;">
        <h4 style="margin:0 0 8px 0; color:#1E293B;">🏠 Dashboard</h4>
        <p style="color:#64748B; font-size:13px; margin:0 0 10px 0;">Gráficos gerenciais, faturamento, alertas críticos e métricas de satisfação.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Acessar Dashboard", key="btn_dash", use_container_width=True):
        st.switch_page("pages/1_🏠_Dashboard.py")

with mcol2:
    st.markdown("""
    <div class="metric-card" style="min-height: 150px;">
        <h4 style="margin:0 0 8px 0; color:#1E293B;">👥 Clientes</h4>
        <p style="color:#64748B; font-size:13px; margin:0 0 10px 0;">Cadastro completo, histórico de pedidos, contatos e histórico de ocorrências.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Gerenciar Clientes", key="btn_cli", use_container_width=True):
        st.switch_page("pages/2_👥_Clientes.py")

with mcol3:
    st.markdown("""
    <div class="metric-card" style="min-height: 150px;">
        <h4 style="margin:0 0 8px 0; color:#1E293B;">📦 Pedidos</h4>
        <p style="color:#64748B; font-size:13px; margin:0 0 10px 0;">Controle de pedidos, atualização de status e rastreamento logístico.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ver Pedidos", key="btn_ped", use_container_width=True):
        st.switch_page("pages/3_📦_Pedidos.py")

with mcol4:
    st.markdown("""
    <div class="metric-card" style="min-height: 150px;">
        <h4 style="margin:0 0 8px 0; color:#1E293B;">⚠️ Problemas</h4>
        <p style="color:#64748B; font-size:13px; margin:0 0 10px 0;">Central de ocorrências de pós-venda, devoluções, atrasos e trocas.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ver Ocorrências", key="btn_prob", use_container_width=True):
        st.switch_page("pages/4_⚠️_Problemas.py")

st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
mcol5, mcol6, mcol7, mcol8 = st.columns(4)

with mcol5:
    st.markdown("""
    <div class="metric-card" style="min-height: 150px;">
        <h4 style="margin:0 0 8px 0; color:#1E293B;">💬 Atendimentos</h4>
        <p style="color:#64748B; font-size:13px; margin:0 0 10px 0;">SAC multicanal (WhatsApp, Mercado Livre, Shopee) com geração de respostas.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Abrir SAC", key="btn_atend", use_container_width=True):
        st.switch_page("pages/5_💬_Atendimentos.py")

with mcol6:
    st.markdown("""
    <div class="metric-card" style="min-height: 150px;">
        <h4 style="margin:0 0 8px 0; color:#1E293B;">🤖 Assistente IA</h4>
        <p style="color:#64748B; font-size:13px; margin:0 0 10px 0;">Chatbot inteligente, análise de sentimento e refinamento de mensagens com Gemini.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Usar Assistente IA", key="btn_ia", use_container_width=True):
        st.switch_page("pages/6_🤖_Assistente_IA.py")

with mcol7:
    st.markdown("""
    <div class="metric-card" style="min-height: 150px;">
        <h4 style="margin:0 0 8px 0; color:#1E293B;">📋 Respostas Prontas</h4>
        <p style="color:#64748B; font-size:13px; margin:0 0 10px 0;">Banco de modelos rápidos com variáveis dinâmicas para agilizar o suporte.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ver Templates", key="btn_resp", use_container_width=True):
        st.switch_page("pages/7_📋_Respostas_Prontas.py")

with mcol8:
    st.markdown("""
    <div class="metric-card" style="min-height: 150px;">
        <h4 style="margin:0 0 8px 0; color:#1E293B;">🔎 Busca Global</h4>
        <p style="color:#64748B; font-size:13px; margin:0 0 10px 0;">Pesquisa unificada em clientes, pedidos, chamados e respostas com 1 clique.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Pesquisar Sistema", key="btn_busca", use_container_width=True):
        st.switch_page("pages/8_🔎_Busca.py")

st.markdown("<br>", unsafe_allow_html=True)

# 8. Visão Operacional Recente
tcol1, tcol2 = st.columns(2)

with tcol1:
    st.markdown("### 💬 **Atendimentos Recentes Pendentes**")
    atendimentos_pendentes = get_atendimentos(status="Pendente")
    if atendimentos_pendentes:
        for item in atendimentos_pendentes[:4]:
            with st.container():
                st.markdown(f"""
                <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:12px; margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <strong>{item['cliente_nome']}</strong>
                        <span>{get_sentiment_badge(item['sentimento'])}</span>
                    </div>
                    <div style="color:#64748B; font-size:13px; margin-top:4px;"><strong>Canal:</strong> {item['canal']} • <strong>Assunto:</strong> {item['assunto']}</div>
                    <div style="background:#F8FAFC; padding:8px; border-radius:6px; font-size:12px; margin-top:6px; color:#334155;">
                        "{item['mensagem_cliente'][:120]}..."
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Nenhum atendimento pendente no momento! 🎉")

with tcol2:
    st.markdown("### ⚠️ **Ocorrências Críticas / Recentes**")
    problemas_abertos = get_problemas(status="Aberto")
    if problemas_abertos:
        for prob in problemas_abertos[:4]:
            with st.container():
                st.markdown(f"""
                <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:12px; margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <strong>{prob['tipo_problema']}</strong>
                        <span>{get_priority_badge(prob['prioridade'])}</span>
                    </div>
                    <div style="color:#64748B; font-size:13px; margin-top:4px;"><strong>Cliente:</strong> {prob['cliente_nome']} • <strong>Pedido:</strong> {prob.get('codigo_pedido') or 'N/A'}</div>
                    <div style="font-size:12px; margin-top:6px; color:#334155;">
                        {prob['descricao'][:120]}...
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.success("Nenhuma ocorrência crítica aberta! Tudo em dia. ✨")
