import streamlit as st
import pandas as pd
from database import search_global
from utils.helpers import (
    apply_custom_css, 
    format_currency, 
    format_date, 
    format_phone,
    get_status_badge,
    get_priority_badge,
    get_sentiment_badge
)

st.set_page_config(page_title="Busca Global • EcomControl", page_icon="🔎", layout="wide")
apply_custom_css()

st.markdown("""
<div class="hero-container">
    <div class="hero-title">🔎 Busca Global Unificada</div>
    <div class="hero-subtitle">Pesquise em todo o sistema simultaneamente por nomes, CPFs, códigos de pedido, rastreios, assuntos e ocorrências.</div>
</div>
""", unsafe_allow_html=True)

# 1. Campo de Busca Central
termo_busca = st.text_input("🔍 Digite sua busca no sistema:", placeholder="Ex: Lucas, PED-2026, teclado, atraso, rastreio...", value="")

if termo_busca and len(termo_busca.strip()) >= 2:
    resultados = search_global(termo_busca)
    
    total_encontrado = (
        len(resultados["clientes"]) +
        len(resultados["pedidos"]) +
        len(resultados["problemas"]) +
        len(resultados["atendimentos"]) +
        len(resultados["respostas"])
    )
    
    st.markdown(f"### 🎯 Resultados da pesquisa para: **'{termo_busca}'** (`{total_encontrado}` itens)")
    
    if total_encontrado == 0:
        st.warning("Nenhum registro encontrado correspondente ao termo pesquisado.")
    else:
        # Abas de resultados categorizados
        tab_c, tab_p, tab_pr, tab_at, tab_rp = st.tabs([
            f"👥 Clientes ({len(resultados['clientes'])})",
            f"📦 Pedidos ({len(resultados['pedidos'])})",
            f"⚠️ Ocorrências ({len(resultados['problemas'])})",
            f"💬 Atendimentos ({len(resultados['atendimentos'])})",
            f"📋 Respostas Prontas ({len(resultados['respostas'])})"
        ])
        
        # Clientes
        with tab_c:
            if resultados["clientes"]:
                df_c = pd.DataFrame([{
                    "ID": c["id"],
                    "Nome": c["nome"],
                    "E-mail": c["email"],
                    "Telefone": format_phone(c["telefone"]),
                    "Cidade/UF": f"{c['cidade'] or '-'}/{c['estado'] or '-'}",
                    "Cadastrado": format_date(c["criado_em"])
                } for c in resultados["clientes"]])
                st.dataframe(df_c, use_container_width=True, hide_index=True)
            else:
                st.caption("Nenhum cliente correspondente.")
                
        # Pedidos
        with tab_p:
            if resultados["pedidos"]:
                df_ped = pd.DataFrame([{
                    "Código": p["codigo_pedido"],
                    "Cliente": p["cliente_nome"],
                    "Produto": p["produto"],
                    "Qtd": p["quantidade"],
                    "Valor": format_currency(p["valor_total"]),
                    "Status": p["status"],
                    "Rastreio": p["codigo_rastreio"] or "-",
                    "Data": format_date(p["data_pedido"])
                } for p in resultados["pedidos"]])
                st.dataframe(df_ped, use_container_width=True, hide_index=True)
            else:
                st.caption("Nenhum pedido correspondente.")
                
        # Ocorrências
        with tab_pr:
            if resultados["problemas"]:
                for pr in resultados["problemas"]:
                    st.markdown(f"""
                    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:14px; margin-bottom:10px;">
                        <div style="display:flex; justify-content:space-between;">
                            <strong>#{pr['id']} - {pr['tipo_problema']}</strong>
                            <span>{get_priority_badge(pr['prioridade'])} {get_status_badge(pr['status'])}</span>
                        </div>
                        <div style="color:#64748B; font-size:13px; margin:4px 0;"><strong>Cliente:</strong> {pr['cliente_nome']} • <strong>Pedido:</strong> {pr.get('codigo_pedido') or '-'}</div>
                        <div style="font-size:13px; color:#334155; margin-top:6px;">{pr['descricao']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("Nenhuma ocorrência correspondente.")
                
        # Atendimentos
        with tab_at:
            if resultados["atendimentos"]:
                for at in resultados["atendimentos"]:
                    st.markdown(f"""
                    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:14px; margin-bottom:10px;">
                        <div style="display:flex; justify-content:space-between;">
                            <strong>#{at['id']} - {at['assunto']} ({at['canal']})</strong>
                            <span>{get_sentiment_badge(at['sentimento'])} {get_status_badge(at['status'])}</span>
                        </div>
                        <div style="color:#64748B; font-size:13px; margin:4px 0;"><strong>Cliente:</strong> {at['cliente_nome']} • <strong>Pedido:</strong> {at.get('codigo_pedido') or '-'}</div>
                        <div style="font-size:13px; background:#F8FAFC; padding:8px; border-radius:6px; margin-top:6px; color:#1E293B;">"{at['mensagem_cliente']}"</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("Nenhum atendimento correspondente.")
                
        # Respostas Prontas
        with tab_rp:
            if resultados["respostas"]:
                for rp in resultados["respostas"]:
                    st.markdown(f"""
                    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:14px; margin-bottom:10px;">
                        <strong>📌 {rp['titulo']}</strong> ({rp['categoria']}) • <code>{rp['atalho'] or '-'}</code>
                        <div style="margin-top:6px; font-size:13px; color:#334155;">{rp['conteudo']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("Nenhum template correspondente.")

else:
    st.info("💡 Digite pelo menos 2 caracteres na caixa acima para realizar a busca em tempo real.")
    
    # Sugestões rápidas de pesquisa
    st.markdown("#### 💡 **Termos sugeridos para teste:**")
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        st.markdown("- `Mariana` (Cliente)")
        st.markdown("- `Carlos` (Cliente)")
    with sc2:
        st.markdown("- `PED-2026-1001` (Pedido)")
        st.markdown("- `Teclado` (Produto)")
    with sc3:
        st.markdown("- `Atraso` (Problema)")
        st.markdown("- `Garantia` (Ocorrência)")
    with sc4:
        st.markdown("- `WhatsApp` (Canal SAC)")
        st.markdown("- `/rastreio` (Template)")
