import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import get_kpis, get_pedidos, get_problemas, get_atendimentos, get_connection
from utils.helpers import (
    apply_custom_css, 
    format_currency, 
    format_date, 
    get_status_badge, 
    get_priority_badge,
    get_sentiment_badge
)

st.set_page_config(page_title="Dashboard • EcomControl", page_icon="🏠", layout="wide")
apply_custom_css()

st.markdown("""
<div class="hero-container">
    <div class="hero-title">🏠 Painel Executivo & Dashboard de Performance</div>
    <div class="hero-subtitle">Visão 360° de faturamento, volume de pedidos, eficiência de suporte e índice de resolução de pós-venda.</div>
</div>
""", unsafe_allow_html=True)

# 1. Carrega Métricas Globais
kpis = get_kpis()

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric(label="💰 Faturamento Total", value=format_currency(kpis['faturamento_total']), delta=f"Ticket: {format_currency(kpis['ticket_medio'])}")
with col2:
    st.metric(label="📦 Total de Pedidos", value=kpis['total_pedidos'], delta=f"{kpis['pedidos_entregues']} entregues")
with col3:
    st.metric(label="⚠️ Problemas Abertos", value=kpis['problemas_abertos'], delta=f"{kpis['problemas_urgentes']} urgentes", delta_color="inverse")
with col4:
    st.metric(label="💬 SAC Pendente", value=kpis['atendimentos_pendentes'], delta=f"{kpis['atendimentos_respondidos']} respondidos")
with col5:
    st.metric(label="🎯 Taxa de Resolução", value=f"{kpis['taxa_resolucao']}%", delta="Meta: > 85%")

st.markdown("<br>", unsafe_allow_html=True)

# 2. Dados para Gráficos
pedidos = get_pedidos()
problemas = get_problemas()
atendimentos = get_atendimentos()

df_pedidos = pd.DataFrame(pedidos) if pedidos else pd.DataFrame()
df_problemas = pd.DataFrame(problemas) if problemas else pd.DataFrame()
df_atendimentos = pd.DataFrame(atendimentos) if atendimentos else pd.DataFrame()

# 3. Gráficos - Linha 1
gcol1, gcol2 = st.columns([6, 4])

with gcol1:
    st.markdown("### 📈 **Evolução de Pedidos & Faturamento**")
    if not df_pedidos.empty:
        df_pedidos["data_dia"] = pd.to_datetime(df_pedidos["data_pedido"]).dt.strftime("%d/%m")
        pedidos_agrupados = df_pedidos.groupby("data_dia").agg(
            total_vendas=('valor_total', 'sum'),
            qtd_pedidos=('id', 'count')
        ).reset_index()

        fig_vendas = go.Figure()
        fig_vendas.add_trace(go.Bar(
            x=pedidos_agrupados["data_dia"], 
            y=pedidos_agrupados["total_vendas"],
            name="Faturamento (R$)",
            marker_color="#3B82F6"
        ))
        fig_vendas.add_trace(go.Scatter(
            x=pedidos_agrupados["data_dia"], 
            y=pedidos_agrupados["qtd_pedidos"],
            name="Qtd Pedidos",
            yaxis="y2",
            mode="lines+markers",
            line=dict(color="#10B981", width=3)
        ))
        fig_vendas.update_layout(
            template="plotly_white",
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis=dict(title="Faturamento (R$)"),
            yaxis2=dict(title="Qtd Pedidos", overlaying="y", side="right")
        )
        st.plotly_chart(fig_vendas, use_container_width=True)
    else:
        st.info("Nenhum dado de vendas registrado.")

with gcol2:
    st.markdown("### 🍩 **Distribuição de Status dos Pedidos**")
    if not df_pedidos.empty:
        status_counts = df_pedidos["status"].value_counts().reset_index()
        status_counts.columns = ["status", "quantidade"]
        
        color_map = {
            "Entregue": "#10B981",
            "Pago": "#3B82F6",
            "Enviado": "#6366F1",
            "Pendente": "#F59E0B",
            "Cancelado": "#EF4444"
        }
        
        fig_status = px.pie(
            status_counts, 
            names="status", 
            values="quantidade", 
            hole=0.55,
            color="status",
            color_discrete_map=color_map
        )
        fig_status.update_layout(
            template="plotly_white",
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(orientation="h", y=-0.1)
        )
        st.plotly_chart(fig_status, use_container_width=True)
    else:
        st.info("Sem dados de pedidos.")

# 4. Gráficos - Linha 2
st.markdown("<br>", unsafe_allow_html=True)
gcol3, gcol4, gcol5 = st.columns(3)

with gcol3:
    st.markdown("### ⚠️ **Principais Motivos de Problemas**")
    if not df_problemas.empty:
        prob_counts = df_problemas["tipo_problema"].value_counts().reset_index()
        prob_counts.columns = ["tipo", "total"]
        fig_prob = px.bar(
            prob_counts,
            x="total",
            y="tipo",
            orientation="h",
            color="total",
            color_continuous_scale="Reds",
            text="total"
        )
        fig_prob.update_layout(
            template="plotly_white",
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="Ocorrências",
            yaxis_title=None
        )
        st.plotly_chart(fig_prob, use_container_width=True)
    else:
        st.info("Nenhuma ocorrência registrada.")

with gcol4:
    st.markdown("### 📱 **Canais de Atendimento (SAC)**")
    if not df_atendimentos.empty:
        canal_counts = df_atendimentos["canal"].value_counts().reset_index()
        canal_counts.columns = ["canal", "total"]
        fig_canais = px.bar(
            canal_counts,
            x="canal",
            y="total",
            color="canal",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_canais.update_layout(
            template="plotly_white",
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="Canal",
            yaxis_title="Total Tickets"
        )
        st.plotly_chart(fig_canais, use_container_width=True)
    else:
        st.info("Nenhum atendimento registrado.")

with gcol5:
    st.markdown("### 🎭 **Sentimento dos Clientes**")
    if not df_atendimentos.empty:
        sent_counts = df_atendimentos["sentimento"].value_counts().reset_index()
        sent_counts.columns = ["sentimento", "total"]
        sent_colors = {
            "Positivo": "#10B981",
            "Neutro": "#3B82F6",
            "Negativo": "#F59E0B",
            "Crítico": "#EF4444"
        }
        fig_sent = px.pie(
            sent_counts,
            names="sentimento",
            values="total",
            color="sentimento",
            color_discrete_map=sent_colors,
            hole=0.4
        )
        fig_sent.update_layout(
            template="plotly_white",
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", y=-0.1)
        )
        st.plotly_chart(fig_sent, use_container_width=True)
    else:
        st.info("Sem dados de sentimento.")

# 5. Tabela de Alertas de Ocorrências Abertas
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 🚨 **Acompanhamento de Ocorrências em Aberto**")
abertos = [p for p in problemas if p["status"] != "Resolvido"]

if abertos:
    table_data = []
    for item in abertos:
        table_data.append({
            "ID": f"#{item['id']}",
            "Cliente": item['cliente_nome'],
            "Pedido": item.get('codigo_pedido') or "N/A",
            "Tipo": item['tipo_problema'],
            "Prioridade": item['prioridade'],
            "Status": item['status'],
            "Data": format_date(item['criado_em'])
        })
    df_tabela = pd.DataFrame(table_data)
    st.dataframe(df_tabela, use_container_width=True, hide_index=True)
else:
    st.success("🎉 Nenhuma ocorrência crítica pendente de resolução!")
