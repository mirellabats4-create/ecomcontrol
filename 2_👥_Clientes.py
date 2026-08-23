import streamlit as st
import pandas as pd
from database import (
    get_clientes, 
    get_cliente_by_id, 
    add_cliente, 
    update_cliente, 
    delete_cliente,
    get_pedidos,
    get_problemas,
    get_atendimentos
)
from utils.helpers import (
    apply_custom_css, 
    format_phone, 
    format_cpf, 
    format_cep, 
    format_date, 
    format_currency,
    export_to_csv,
    get_status_badge
)

st.set_page_config(page_title="Clientes • EcomControl", page_icon="👥", layout="wide")
apply_custom_css()

st.markdown("""
<div class="hero-container">
    <div class="hero-title">👥 Gestão da Base de Clientes</div>
    <div class="hero-subtitle">Consulte o histórico de pedidos, compras, chamados de suporte e gerencie dados cadastrais.</div>
</div>
""", unsafe_allow_html=True)

tab_lista, tab_novo, tab_editar = st.tabs(["📋 Consulta de Clientes", "➕ Novo Cliente", "✏️ Gerenciar / Excluir"])

# ==========================================
# ABA 1: CONSULTA DE CLIENTES
# ==========================================
with tab_lista:
    col_search, col_exp = st.columns([8, 2])
    with col_search:
        search_query = st.text_input("🔍 Pesquisar por Nome, E-mail, CPF ou Telefone:", placeholder="Digite para filtrar...")
    
    clientes = get_clientes(search=search_query if search_query else None)
    
    with col_exp:
        st.markdown("<br>", unsafe_allow_html=True)
        if clientes:
            df_exp = pd.DataFrame(clientes)
            csv_data = export_to_csv(df_exp)
            st.download_button(
                label="📥 Exportar CSV",
                data=csv_data,
                file_name="clientes_ecomcontrol.csv",
                mime="text/csv",
                use_container_width=True
            )
            
    st.markdown(f"**Total de registros encontrados:** `{len(clientes)}`")
    
    if clientes:
        # Tabela formatada para visualização
        data_view = []
        for c in clientes:
            data_view.append({
                "ID": c["id"],
                "Nome": c["nome"],
                "E-mail": c["email"],
                "Telefone": format_phone(c["telefone"]),
                "CPF": format_cpf(c["cpf"]),
                "Cidade/UF": f"{c['cidade'] or '-'}/{c['estado'] or '-'}",
                "Cadastrado em": format_date(c["criado_em"])
            })
        
        df_clientes = pd.DataFrame(data_view)
        st.dataframe(df_clientes, use_container_width=True, hide_index=True)
        
        st.divider()
        st.markdown("### 🔎 **Ficha Detalhada do Cliente**")
        
        cli_options = {c["id"]: f"{c['nome']} (ID #{c['id']} - {c['email']})" for c in clientes}
        selected_id = st.selectbox("Selecione um cliente para ver o histórico completo:", options=list(cli_options.keys()), format_func=lambda x: cli_options[x])
        
        if selected_id:
            cliente_info = get_cliente_by_id(selected_id)
            pedidos_cliente = get_pedidos(cliente_id=selected_id)
            problemas_cliente = [p for p in get_problemas() if p.get("cliente_id") == selected_id]
            atendimentos_cliente = [a for a in get_atendimentos() if a.get("cliente_id") == selected_id]
            
            c_info1, c_info2, c_info3 = st.columns(3)
            with c_info1:
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin:0 0 10px 0; color:#1E293B;">👤 Dados Pessoais</h4>
                    <p style="margin:4px 0; font-size:14px;"><strong>Nome:</strong> {cliente_info['nome']}</p>
                    <p style="margin:4px 0; font-size:14px;"><strong>CPF:</strong> {format_cpf(cliente_info['cpf'])}</p>
                    <p style="margin:4px 0; font-size:14px;"><strong>Email:</strong> {cliente_info['email']}</p>
                    <p style="margin:4px 0; font-size:14px;"><strong>Telefone:</strong> {format_phone(cliente_info['telefone'])}</p>
                </div>
                """, unsafe_allow_html=True)
                
            with c_info2:
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin:0 0 10px 0; color:#1E293B;">📍 Endereço de Entrega</h4>
                    <p style="margin:4px 0; font-size:14px;"><strong>Endereço:</strong> {cliente_info['endereco'] or '-'}</p>
                    <p style="margin:4px 0; font-size:14px;"><strong>Cidade/UF:</strong> {cliente_info['cidade'] or '-'}/{cliente_info['estado'] or '-'}</p>
                    <p style="margin:4px 0; font-size:14px;"><strong>CEP:</strong> {format_cep(cliente_info['cep'])}</p>
                    <p style="margin:4px 0; font-size:14px;"><strong>Cliente desde:</strong> {format_date(cliente_info['criado_em'])}</p>
                </div>
                """, unsafe_allow_html=True)
                
            with c_info3:
                total_gasto = sum([p['valor_total'] for p in pedidos_cliente]) if pedidos_cliente else 0.0
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin:0 0 10px 0; color:#1E293B;">📊 Resumo Comercial</h4>
                    <p style="margin:4px 0; font-size:14px;"><strong>Total de Pedidos:</strong> {len(pedidos_cliente)}</p>
                    <p style="margin:4px 0; font-size:14px;"><strong>LTV (Total Gasto):</strong> {format_currency(total_gasto)}</p>
                    <p style="margin:4px 0; font-size:14px;"><strong>Chamados de Pós-venda:</strong> {len(problemas_cliente)}</p>
                    <p style="margin:4px 0; font-size:14px;"><strong>Tickets de SAC:</strong> {len(atendimentos_cliente)}</p>
                </div>
                """, unsafe_allow_html=True)
                
            # Histórico de Pedidos do Cliente
            st.markdown("#### 📦 Histórico de Pedidos")
            if pedidos_cliente:
                df_ped_cli = pd.DataFrame([{
                    "Pedido": p["codigo_pedido"],
                    "Produto": p["produto"],
                    "Qtd": p["quantidade"],
                    "Valor": format_currency(p["valor_total"]),
                    "Status": p["status"],
                    "Rastreio": p["codigo_rastreio"] or "-",
                    "Data": format_date(p["data_pedido"])
                } for p in pedidos_cliente])
                st.dataframe(df_ped_cli, use_container_width=True, hide_index=True)
            else:
                st.caption("Nenhum pedido registrado para este cliente.")
                
    else:
        st.warning("Nenhum cliente cadastrado ou encontrado na busca.")

# ==========================================
# ABA 2: NOVO CLIENTE
# ==========================================
with tab_novo:
    st.markdown("### ➕ **Cadastro de Novo Cliente**")
    with st.form("form_novo_cliente", clear_on_submit=True):
        col_n1, col_n2 = st.columns(2)
        with col_n1:
            novo_nome = st.text_input("Nome Completo: *", placeholder="Ex: Mariana Costa")
            novo_email = st.text_input("E-mail: *", placeholder="Ex: mariana@email.com")
            novo_telefone = st.text_input("Telefone / WhatsApp:", placeholder="Ex: 11987654321")
            novo_cpf = st.text_input("CPF:", placeholder="Ex: 12345678900")
            
        with col_n2:
            novo_endereco = st.text_input("Endereço Completo:", placeholder="Ex: Av. Paulista, 1000, Apto 50")
            novo_cidade = st.text_input("Cidade:", placeholder="Ex: São Paulo")
            novo_estado = st.selectbox("Estado (UF):", ["SP", "RJ", "MG", "PR", "RS", "SC", "BA", "CE", "DF", "GO", "PE", "ES", "Outro"])
            novo_cep = st.text_input("CEP:", placeholder="Ex: 01310100")
            
        submitted_novo = st.form_submit_button("💾 Salvar Cliente", use_container_width=True)
        
        if submitted_novo:
            if not novo_nome or not novo_email:
                st.error("Por favor, preencha os campos obrigatórios (Nome e E-mail)!")
            else:
                novo_id = add_cliente(
                    nome=novo_nome,
                    email=novo_email,
                    telefone=novo_telefone,
                    cpf=novo_cpf,
                    endereco=novo_endereco,
                    cidade=novo_cidade,
                    estado=novo_estado,
                    cep=novo_cep
                )
                st.success(f"🎉 Cliente **{novo_nome}** cadastrado com sucesso com ID #{novo_id}!")
                st.rerun()

# ==========================================
# ABA 3: EDITAR / EXCLUIR
# ==========================================
with tab_editar:
    st.markdown("### ✏️ **Editar ou Remover Cliente**")
    todos_clientes = get_clientes()
    
    if todos_clientes:
        dict_edit = {c["id"]: f"{c['nome']} (ID #{c['id']})" for c in todos_clientes}
        sel_edit_id = st.selectbox("Selecione o cliente para gerenciar:", options=list(dict_edit.keys()), format_func=lambda x: dict_edit[x], key="sel_edit_cli")
        
        cli_edit = get_cliente_by_id(sel_edit_id)
        if cli_edit:
            with st.form("form_edit_cliente"):
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    e_nome = st.text_input("Nome:", value=cli_edit["nome"])
                    e_email = st.text_input("E-mail:", value=cli_edit["email"])
                    e_telefone = st.text_input("Telefone:", value=cli_edit["telefone"] or "")
                    e_cpf = st.text_input("CPF:", value=cli_edit["cpf"] or "")
                with col_e2:
                    e_endereco = st.text_input("Endereço:", value=cli_edit["endereco"] or "")
                    e_cidade = st.text_input("Cidade:", value=cli_edit["cidade"] or "")
                    ufs = ["SP", "RJ", "MG", "PR", "RS", "SC", "BA", "CE", "DF", "GO", "PE", "ES", "Outro"]
                    uf_idx = ufs.index(cli_edit["estado"]) if cli_edit["estado"] in ufs else 0
                    e_estado = st.selectbox("Estado (UF):", ufs, index=uf_idx)
                    e_cep = st.text_input("CEP:", value=cli_edit["cep"] or "")
                    
                col_btn1, col_btn2 = st.columns([7, 3])
                with col_btn1:
                    sub_edit = st.form_submit_button("🔄 Atualizar Dados Cadastrais", use_container_width=True)
                with col_btn2:
                    sub_del = st.form_submit_button("🗑️ Excluir Cliente", type="secondary", use_container_width=True)
                    
                if sub_edit:
                    update_cliente(
                        cliente_id=sel_edit_id,
                        nome=e_nome,
                        email=e_email,
                        telefone=e_telefone,
                        cpf=e_cpf,
                        endereco=e_endereco,
                        cidade=e_cidade,
                        estado=e_estado,
                        cep=e_cep
                    )
                    st.success("✅ Dados atualizados com sucesso!")
                    st.rerun()
                    
                if sub_del:
                    delete_cliente(sel_edit_id)
                    st.warning(f"🗑️ Cliente removido do sistema!")
                    st.rerun()
    else:
        st.info("Nenhum cliente disponível para edição.")
