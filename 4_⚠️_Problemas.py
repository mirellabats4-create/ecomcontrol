import streamlit as st
import pandas as pd
from database import (
    get_problemas, 
    get_problema_by_id, 
    add_problema, 
    update_problema, 
    delete_problema,
    get_clientes,
    get_pedidos
)
from utils.helpers import (
    apply_custom_css, 
    format_date, 
    get_status_badge, 
    get_priority_badge,
    export_to_csv
)

st.set_page_config(page_title="Problemas • EcomControl", page_icon="⚠️", layout="wide")
apply_custom_css()

st.markdown("""
<div class="hero-container">
    <div class="hero-title">⚠️ Central de Ocorrências & Pós-Venda</div>
    <div class="hero-subtitle">Gerencie reclamações, atrasos logísticos, extravios, produtos com avaria e pedidos de cancelamento/estorno.</div>
</div>
""", unsafe_allow_html=True)

# 1. Contadores Rápidos
problemas_todos = get_problemas()
total_p = len(problemas_todos)
abertos = len([p for p in problemas_todos if p["status"] == "Aberto"])
analise = len([p for p in problemas_todos if p["status"] == "Em Análise"])
resolvidos = len([p for p in problemas_todos if p["status"] == "Resolvido"])
urgentes = len([p for p in problemas_todos if p["prioridade"] == "Urgente" and p["status"] != "Resolvido"])

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total Ocorrências", total_p)
m2.metric("🚨 Urgentes", urgentes)
m3.metric("🔴 Em Aberto", abertos)
m4.metric("🟡 Em Análise", analise)
m5.metric("🟢 Resolvidos", resolvidos)

st.markdown("<br>", unsafe_allow_html=True)

tab_lista, tab_novo, tab_editar = st.tabs(["📋 Todas as Ocorrências", "➕ Registrar Ocorrência", "🛠️ Atualizar / Solucionar"])

# ==========================================
# ABA 1: TODAS AS OCORRÊNCIAS
# ==========================================
with tab_lista:
    c_f1, c_f2, c_f3, c_f4 = st.columns([3, 3, 4, 2])
    with c_f1:
        f_status = st.selectbox("Status:", ["Todos", "Aberto", "Em Análise", "Resolvido"])
    with c_f2:
        f_prioridade = st.selectbox("Prioridade:", ["Todas", "Urgente", "Alta", "Média", "Baixa"])
    with c_f3:
        f_search = st.text_input("🔍 Buscar:", placeholder="Cliente, pedido ou motivo...")
    with c_f4:
        st.markdown("<br>", unsafe_allow_html=True)
        prob_filtrados = get_problemas(
            status=f_status if f_status != "Todos" else None,
            prioridade=f_prioridade if f_prioridade != "Todas" else None,
            search=f_search if f_search else None
        )
        if prob_filtrados:
            st.download_button("📥 Exportar", data=export_to_csv(pd.DataFrame(prob_filtrados)), file_name="ocorrencias.csv", use_container_width=True)

    st.markdown(f"**Registros encontrados:** `{len(prob_filtrados)}`")
    
    if prob_filtrados:
        data_view = []
        for pr in prob_filtrados:
            data_view.append({
                "ID": f"#{pr['id']}",
                "Cliente": pr["cliente_nome"],
                "Pedido": pr.get("codigo_pedido") or "-",
                "Tipo": pr["tipo_problema"],
                "Prioridade": pr["prioridade"],
                "Status": pr["status"],
                "Registrado em": format_date(pr["criado_em"])
            })
        
        st.dataframe(pd.DataFrame(data_view), use_container_width=True, hide_index=True)
        
        st.divider()
        st.markdown("### 🔎 **Ficha de Detalhe da Ocorrência**")
        prob_map = {pr["id"]: f"#{pr['id']} - {pr['tipo_problema']} ({pr['cliente_nome']})" for pr in prob_filtrados}
        sel_pr_id = st.selectbox("Selecione para inspecionar:", options=list(prob_map.keys()), format_func=lambda x: prob_map[x])
        
        if sel_pr_id:
            pr_detalhe = get_problema_by_id(sel_pr_id)
            c1, c2 = st.columns([6, 4])
            with c1:
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin:0 0 8px 0; color:#1E293B;">📝 Relato do Problema</h4>
                    <p style="margin:4px 0;"><strong>Tipo:</strong> {pr_detalhe['tipo_problema']}</p>
                    <p style="margin:4px 0;"><strong>Prioridade:</strong> {get_priority_badge(pr_detalhe['prioridade'])} &nbsp; <strong>Status:</strong> {get_status_badge(pr_detalhe['status'])}</p>
                    <div style="background:#F8FAFC; padding:12px; border-radius:8px; border:1px solid #E2E8F0; margin-top:10px; font-size:14px; color:#334155;">
                        {pr_detalhe['descricao']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin:0 0 8px 0; color:#1E293B;">👤 Cliente & Pedido</h4>
                    <p style="margin:4px 0;"><strong>Cliente:</strong> {pr_detalhe['cliente_nome']}</p>
                    <p style="margin:4px 0;"><strong>E-mail:</strong> {pr_detalhe['cliente_email']}</p>
                    <p style="margin:4px 0;"><strong>Pedido:</strong> {pr_detalhe.get('codigo_pedido') or 'Nenhum pedido vinculado'}</p>
                    <p style="margin:4px 0;"><strong>Produto:</strong> {pr_detalhe.get('pedido_produto') or '-'}</p>
                    <p style="margin:4px 0;"><strong>Aberto em:</strong> {format_date(pr_detalhe['criado_em'])}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Nenhuma ocorrência encontrada com os filtros atuais.")

# ==========================================
# ABA 2: REGISTRAR OCORRÊNCIA
# ==========================================
with tab_novo:
    st.markdown("### ➕ **Abrir Nova Ocorrência**")
    clientes = get_clientes()
    pedidos = get_pedidos()
    
    if not clientes:
        st.warning("Cadastre clientes antes de registrar ocorrências.")
    else:
        with st.form("form_novo_problema", clear_on_submit=True):
            col_o1, col_o2 = st.columns(2)
            with col_o1:
                cli_dict = {c["id"]: f"{c['nome']} ({c['email']})" for c in clientes}
                sel_cli_id = st.selectbox("Cliente Afetado: *", options=list(cli_dict.keys()), format_func=lambda x: cli_dict[x])
                
                ped_dict = {0: "Nenhum (Dúvida / Pré-venda / Outro)"}
                for p in pedidos:
                    ped_dict[p["id"]] = f"{p['codigo_pedido']} - {p['produto']} ({p['cliente_nome']})"
                sel_ped_id = st.selectbox("Pedido Relacionado (Opcional):", options=list(ped_dict.keys()), format_func=lambda x: ped_dict[x])
                
                tipo_prob = st.selectbox("Tipo de Ocorrência: *", [
                    "Atraso na Entrega",
                    "Defeito de Fabricação",
                    "Extravio de Encomenda",
                    "Item Incorreto / Faltando",
                    "Cancelamento / Reembolso",
                    "Produto Avariado no Transporte",
                    "Dúvida / Suporte Técnico",
                    "Outro"
                ])
                
            with col_o2:
                prioridade = st.selectbox("Nível de Prioridade:", ["Baixa", "Média", "Alta", "Urgente"], index=1)
                status_ini = st.selectbox("Status Inicial:", ["Aberto", "Em Análise", "Resolvido"], index=0)
                descricao = st.text_area("Descrição Detalhada do Problema / Relato do Cliente: *", placeholder="Explique os detalhes do ocorrido...", height=120)
                
            sub_prob = st.form_submit_button("💾 Registrar Ocorrência", use_container_width=True)
            
            if sub_prob:
                if not descricao:
                    st.error("A descrição do problema é obrigatória!")
                else:
                    novo_id = add_problema(
                        cliente_id=sel_cli_id,
                        pedido_id=sel_ped_id if sel_ped_id != 0 else None,
                        tipo_problema=tipo_prob,
                        descricao=descricao,
                        status=status_ini,
                        prioridade=prioridade
                    )
                    st.success(f"🎉 Ocorrência #{novo_id} registrada com sucesso!")
                    st.rerun()

# ==========================================
# ABA 3: ATUALIZAR / SOLUCIONAR
# ==========================================
with tab_editar:
    st.markdown("### 🛠️ **Atualizar Status ou Solucionar Ocorrência**")
    if problemas_todos:
        dict_up_prob = {pr["id"]: f"#{pr['id']} - {pr['tipo_problema']} ({pr['cliente_nome']}) [{pr['status']}]" for pr in problemas_todos}
        sel_pr_edit = st.selectbox("Selecione a ocorrência:", options=list(dict_up_prob.keys()), format_func=lambda x: dict_up_prob[x], key="sel_pr_edit_box")
        
        pr_edit = get_problema_by_id(sel_pr_edit)
        if pr_edit:
            with st.form("form_edit_problema"):
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    tipos = ["Atraso na Entrega", "Defeito de Fabricação", "Extravio de Encomenda", "Item Incorreto / Faltando", "Cancelamento / Reembolso", "Produto Avariado no Transporte", "Dúvida / Suporte Técnico", "Outro"]
                    t_idx = tipos.index(pr_edit["tipo_problema"]) if pr_edit["tipo_problema"] in tipos else 0
                    up_tipo = st.selectbox("Tipo:", tipos, index=t_idx)
                    
                    status_list = ["Aberto", "Em Análise", "Resolvido"]
                    s_idx = status_list.index(pr_edit["status"]) if pr_edit["status"] in status_list else 0
                    up_status = st.selectbox("Status da Ocorrência:", status_list, index=s_idx)
                    
                    priori_list = ["Baixa", "Média", "Alta", "Urgente"]
                    p_idx = priori_list.index(pr_edit["prioridade"]) if pr_edit["prioridade"] in priori_list else 1
                    up_prioridade = st.selectbox("Prioridade:", priori_list, index=p_idx)
                    
                with col_e2:
                    up_desc = st.text_area("Descrição / Notas de Resolução:", value=pr_edit["descricao"], height=160)
                    
                col_b1, col_b2 = st.columns([7, 3])
                with col_b1:
                    btn_save_pr = st.form_submit_button("🔄 Salvar Alterações", use_container_width=True)
                with col_b2:
                    btn_del_pr = st.form_submit_button("🗑️ Excluir Ocorrência", type="secondary", use_container_width=True)
                    
                if btn_save_pr:
                    update_problema(
                        problema_id=sel_pr_edit,
                        tipo_problema=up_tipo,
                        descricao=up_desc,
                        status=up_status,
                        prioridade=up_prioridade,
                        pedido_id=pr_edit.get("pedido_id")
                    )
                    st.success("✅ Ocorrência atualizada com sucesso!")
                    st.rerun()
                    
                if btn_del_pr:
                    delete_problema(sel_pr_edit)
                    st.warning("🗑️ Ocorrência removida!")
                    st.rerun()
    else:
        st.info("Nenhuma ocorrência para gerenciar.")
