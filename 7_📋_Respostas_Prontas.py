import streamlit as st
import pandas as pd
from database import (
    get_respostas_prontas, 
    get_resposta_pronta_by_id, 
    add_resposta_pronta, 
    update_resposta_pronta, 
    delete_resposta_pronta
)
from utils.helpers import apply_custom_css, format_date

st.set_page_config(page_title="Respostas Prontas • EcomControl", page_icon="📋", layout="wide")
apply_custom_css()

st.markdown("""
<div class="hero-container">
    <div class="hero-title">📋 Banco de Respostas Prontas & Templates</div>
    <div class="hero-subtitle">Modelos padronizados com variáveis dinâmicas ({nome}, {pedido}, {codigo_rastreio}) para acelerar o suporte.</div>
</div>
""", unsafe_allow_html=True)

tab_catalogo, tab_novo, tab_gerenciar = st.tabs(["📚 Catálogo de Respostas", "➕ Novo Modelo", "✏️ Gerenciar / Excluir"])

# ==========================================
# ABA 1: CATÁLOGO DE RESPOSTAS
# ==========================================
with tab_catalogo:
    col_c1, col_c2 = st.columns([4, 6])
    with col_c1:
        cat_filtro = st.selectbox("Filtrar por Categoria:", ["Todas", "Rastreio", "Atraso", "Garantia", "Financeiro", "Geral"])
    with col_c2:
        busca_resp = st.text_input("🔍 Pesquisar por Título, Conteúdo ou Atalho (/):", placeholder="Ex: /rastreio ou devolução...")
        
    respostas = get_respostas_prontas(
        categoria=cat_filtro if cat_filtro != "Todas" else None,
        search=busca_resp if busca_resp else None
    )
    
    st.markdown(f"**Total de modelos encontrados:** `{len(respostas)}`")
    
    if respostas:
        # Simulador de Variáveis Interativo
        st.markdown("### 🧪 **Simulador & Copiador de Templates**")
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            sim_nome = st.text_input("Nome para preencher {nome}:", value="Mariana")
        with col_s2:
            sim_pedido = st.text_input("Pedido para {pedido}:", value="PED-2026-1002")
        with col_s3:
            sim_rastreio = st.text_input("Rastreio para {codigo_rastreio}:", value="BR384756291BB")
            
        st.divider()
        
        for r in respostas:
            with st.expander(f"📌 **{r['titulo']}** | Categoria: `{r['categoria']}` | Atalho: `{r['atalho'] or '-'}`", expanded=True):
                conteudo_raw = r["conteudo"]
                
                # Aplica as variáveis
                conteudo_preenchido = (
                    conteudo_raw.replace("{nome}", sim_nome)
                    .replace("{pedido}", sim_pedido)
                    .replace("{codigo_rastreio}", sim_rastreio)
                )
                
                st.markdown(f"""
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:12px; border-radius:8px; font-size:14px; color:#1E293B;">
                    {conteudo_preenchido}
                </div>
                """, unsafe_allow_html=True)
                
                st.text_area("Texto pronto para copiar:", value=conteudo_preenchido, key=f"copy_area_{r['id']}", height=80)
    else:
        st.info("Nenhuma resposta pronta encontrada.")

# ==========================================
# ABA 2: NOVO MODELO
# ==========================================
with tab_novo:
    st.markdown("### ➕ **Cadastrar Nova Resposta Pronta**")
    st.caption("Você pode utilizar as variáveis coringas: `{nome}`, `{pedido}`, `{codigo_rastreio}` no texto.")
    
    with st.form("form_nova_resposta", clear_on_submit=True):
        col_n1, col_n2 = st.columns(2)
        with col_n1:
            novo_titulo = st.text_input("Título do Modelo: *", placeholder="Ex: Solicitação de Comprovante")
            nova_cat = st.selectbox("Categoria: *", ["Rastreio", "Atraso", "Garantia", "Financeiro", "Geral", "Outro"])
            novo_atalho = st.text_input("Atalho de Teclado (Opcional):", placeholder="Ex: /comprovante")
        with col_n2:
            novo_conteudo = st.text_area("Texto / Conteúdo da Mensagem: *", placeholder="Olá {nome}, tudo bem? ...", height=140)
            
        sub_resp = st.form_submit_button("💾 Salvar Template", use_container_width=True)
        
        if sub_resp:
            if not novo_titulo or not novo_conteudo:
                st.error("Título e Conteúdo são obrigatórios!")
            else:
                novo_id = add_resposta_pronta(
                    titulo=novo_titulo,
                    categoria=nova_cat,
                    conteudo=novo_conteudo,
                    atalho=novo_atalho
                )
                st.success(f"🎉 Modelo **{novo_titulo}** adicionado com sucesso (ID #{novo_id})!")
                st.rerun()

# ==========================================
# ABA 3: GERENCIAR / EXCLUIR
# ==========================================
with tab_gerenciar:
    st.markdown("### ✏️ **Editar ou Excluir Template**")
    todas_respostas = get_respostas_prontas()
    
    if todas_respostas:
        dict_edit_r = {r["id"]: f"{r['titulo']} ({r['categoria']}) - {r['atalho'] or ''}" for r in todas_respostas}
        sel_r_id = st.selectbox("Selecione o modelo:", options=list(dict_edit_r.keys()), format_func=lambda x: dict_edit_r[x])
        
        r_item = get_resposta_pronta_by_id(sel_r_id)
        if r_item:
            with st.form("form_edit_template"):
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    e_titulo = st.text_input("Título:", value=r_item["titulo"])
                    cats = ["Rastreio", "Atraso", "Garantia", "Financeiro", "Geral", "Outro"]
                    c_idx = cats.index(r_item["categoria"]) if r_item["categoria"] in cats else 0
                    e_cat = st.selectbox("Categoria:", cats, index=c_idx)
                    e_atalho = st.text_input("Atalho:", value=r_item["atalho"] or "")
                with col_e2:
                    e_conteudo = st.text_area("Conteúdo:", value=r_item["conteudo"], height=140)
                    
                col_b1, col_b2 = st.columns([7, 3])
                with col_b1:
                    btn_up_r = st.form_submit_button("🔄 Atualizar Template", use_container_width=True)
                with col_b2:
                    btn_del_r = st.form_submit_button("🗑️ Excluir Template", type="secondary", use_container_width=True)
                    
                if btn_up_r:
                    update_resposta_pronta(
                        resposta_id=sel_r_id,
                        titulo=e_titulo,
                        categoria=e_cat,
                        conteudo=e_conteudo,
                        atalho=e_atalho
                    )
                    st.success("✅ Template atualizado com sucesso!")
                    st.rerun()
                    
                if btn_del_r:
                    delete_resposta_pronta(sel_r_id)
                    st.warning("🗑️ Template removido!")
                    st.rerun()
    else:
        st.info("Nenhum template cadastrado.")
