import streamlit as st
import pandas as pd
from database import (
    get_pedidos, 
    get_pedido_by_id, 
    add_pedido, 
    update_pedido, 
    delete_pedido,
    get_clientes
)
from utils.helpers import (
    apply_custom_css, 
    format_currency, 
    format_date, 
    export_to_csv,
    get_status_badge
)

st.set_page_config(page_title="Pedidos • EcomControl", page_icon="📦", layout="wide")
apply_custom_css()

st.markdown("""
<div class="hero-container">
    <div class="hero-title">📦 Gestão de Pedidos & Rastreamento</div>
    <div class="hero-subtitle">Controle de fluxo de vendas, códigos de rastreamento logístico e status de entrega.</div>
</div>
""", unsafe_allow_html=True)

tab_lista, tab_novo, tab_atualizar = st.tabs(["📋 Todos os Pedidos", "➕ Novo Pedido", "🔄 Atualizar Status / Rastreio"])

# ==========================================
# ABA 1: LISTA DE PEDIDOS
# ==========================================
with tab_lista:
    col_f1, col_f2, col_f3 = st.columns([4, 4, 2])
    with col_f1:
        filtro_status = st.selectbox("Filtrar por Status:", ["Todos", "Pendente", "Pago", "Enviado", "Entregue", "Cancelado"])
    with col_f2:
        search_ped = st.text_input("🔍 Pesquisar Pedido (Código, Produto, Rastreio ou Cliente):", placeholder="Ex: PED-2026...")
    with col_f3:
        st.markdown("<br>", unsafe_allow_html=True)
        pedidos_raw = get_pedidos(
            status=filtro_status if filtro_status != "Todos" else None,
            search=search_ped if search_ped else None
        )
        if pedidos_raw:
            df_exp = pd.DataFrame(pedidos_raw)
            st.download_button(
                label="📥 Exportar CSV",
                data=export_to_csv(df_exp),
                file_name="pedidos_ecomcontrol.csv",
                mime="text/csv",
                use_container_width=True
            )

    pedidos = get_pedidos(
        status=filtro_status if filtro_status != "Todos" else None,
        search=search_ped if search_ped else None
    )
    
    st.markdown(f"**Total de Pedidos encontrados:** `{len(pedidos)}`")
    
    if pedidos:
        data_view = []
        for p in pedidos:
            data_view.append({
                "ID": f"#{p['id']}",
                "Código": p["codigo_pedido"],
                "Cliente": p["cliente_nome"],
                "Produto": p["produto"],
                "Qtd": p["quantidade"],
                "Valor Total": format_currency(p["valor_total"]),
                "Status": p["status"],
                "Rastreio": p["codigo_rastreio"] or "-",
                "Data": format_date(p["data_pedido"])
            })
        
        df_p = pd.DataFrame(data_view)
        st.dataframe(df_p, use_container_width=True, hide_index=True)
        
        st.divider()
        st.markdown("### 🔍 **Detalhes & Ações Rápidas do Pedido**")
        dict_peds = {p["id"]: f"{p['codigo_pedido']} - {p['cliente_nome']} ({p['produto']})" for p in pedidos}
        sel_ped_id = st.selectbox("Selecione um pedido:", options=list(dict_peds.keys()), format_func=lambda x: dict_peds[x])
        
        if sel_ped_id:
            ped_detalhe = get_pedido_by_id(sel_ped_id)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin:0 0 8px 0; color:#1E293B;">📦 Dados da Venda</h4>
                    <p style="margin:4px 0; font-size:14px;"><strong>Código:</strong> {ped_detalhe['codigo_pedido']}</p>
                    <p style="margin:4px 0; font-size:14px;"><strong>Produto:</strong> {ped_detalhe['produto']}</p>
                    <p style="margin:4px 0; font-size:14px;"><strong>Quantidade:</strong> {ped_detalhe['quantidade']} un.</p>
                    <p style="margin:4px 0; font-size:14px;"><strong>Valor Total:</strong> {format_currency(ped_detalhe['valor_total'])}</p>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin:0 0 8px 0; color:#1E293B;">🚚 Logística & Envio</h4>
                    <p style="margin:4px 0; font-size:14px;"><strong>Status:</strong> {get_status_badge(ped_detalhe['status'])}</p>
                    <p style="margin:4px 0; font-size:14px;"><strong>Rastreamento:</strong> <code>{ped_detalhe['codigo_rastreio'] or 'Não despachado'}</code></p>
                    <p style="margin:4px 0; font-size:14px;"><strong>Data do Pedido:</strong> {format_date(ped_detalhe['data_pedido'])}</p>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin:0 0 8px 0; color:#1E293B;">👤 Comprador</h4>
                    <p style="margin:4px 0; font-size:14px;"><strong>Nome:</strong> {ped_detalhe['cliente_nome']}</p>
                    <p style="margin:4px 0; font-size:14px;"><strong>E-mail:</strong> {ped_detalhe['cliente_email']}</p>
                    <p style="margin:4px 0; font-size:14px;"><strong>Telefone:</strong> {ped_detalhe['cliente_telefone'] or '-'}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Nenhum pedido encontrado com os filtros selecionados.")

# ==========================================
# ABA 2: NOVO PEDIDO
# ==========================================
with tab_novo:
    st.markdown("### ➕ **Cadastrar Novo Pedido**")
    clientes = get_clientes()
    
    if not clientes:
        st.warning("⚠️ Você precisa cadastrar pelo menos um cliente antes de criar um pedido!")
    else:
        with st.form("form_novo_pedido", clear_on_submit=True):
            col_p1, col_p2 = st.columns(2)
            
            with col_p1:
                cli_options = {c["id"]: f"{c['nome']} ({c['email']})" for c in clientes}
                selected_cliente_id = st.selectbox("Cliente: *", options=list(cli_options.keys()), format_func=lambda x: cli_options[x])
                codigo_pedido = st.text_input("Código do Pedido: *", placeholder="Ex: PED-2026-1050")
                produto = st.text_input("Produto / Descrição do Item: *", placeholder="Ex: Fone Bluetooth Sem Fio")
                quantidade = st.number_input("Quantidade:", min_value=1, value=1, step=1)
                
            with col_p2:
                valor_total = st.number_input("Valor Total (R$): *", min_value=0.0, value=99.90, step=10.0, format="%.2f")
                status = st.selectbox("Status Inicial:", ["Pendente", "Pago", "Enviado", "Entregue", "Cancelado"])
                codigo_rastreio = st.text_input("Código de Rastreio (Opcional):", placeholder="Ex: BR123456789AA")
                
            sub_pedido = st.form_submit_button("💾 Salvar Pedido", use_container_width=True)
            
            if sub_pedido:
                if not codigo_pedido or not produto or valor_total <= 0:
                    st.error("Por favor, preencha os campos obrigatórios (Código, Produto e Valor maior que zero)!")
                else:
                    try:
                        novo_id = add_pedido(
                            codigo_pedido=codigo_pedido,
                            cliente_id=selected_cliente_id,
                            produto=produto,
                            quantidade=quantidade,
                            valor_total=valor_total,
                            status=status,
                            codigo_rastreio=codigo_rastreio
                        )
                        st.success(f"🎉 Pedido **{codigo_pedido}** cadastrado com sucesso (ID #{novo_id})!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar pedido: {str(e)}")

# ==========================================
# ABA 3: ATUALIZAR STATUS & RASTREIO
# ==========================================
with tab_atualizar:
    st.markdown("### 🔄 **Atualizar Pedido Existente**")
    todos_pedidos = get_pedidos()
    
    if todos_pedidos:
        dict_up_ped = {p["id"]: f"{p['codigo_pedido']} - {p['cliente_nome']} ({p['produto']}) [Status: {p['status']}]" for p in todos_pedidos}
        sel_ped_up_id = st.selectbox("Selecione o pedido para editar:", options=list(dict_up_ped.keys()), format_func=lambda x: dict_up_ped[x], key="sel_ped_up")
        
        ped_up = get_pedido_by_id(sel_ped_up_id)
        if ped_up:
            with st.form("form_edit_pedido"):
                col_u1, col_u2 = st.columns(2)
                with col_u1:
                    u_codigo = st.text_input("Código do Pedido:", value=ped_up["codigo_pedido"])
                    u_produto = st.text_input("Produto:", value=ped_up["produto"])
                    u_quantidade = st.number_input("Quantidade:", min_value=1, value=int(ped_up["quantidade"]))
                    u_valor = st.number_input("Valor Total (R$):", min_value=0.0, value=float(ped_up["valor_total"]), format="%.2f")
                with col_u2:
                    statuses = ["Pendente", "Pago", "Enviado", "Entregue", "Cancelado"]
                    idx_st = statuses.index(ped_up["status"]) if ped_up["status"] in statuses else 0
                    u_status = st.selectbox("Status Atual:", statuses, index=idx_st)
                    u_rastreio = st.text_input("Código de Rastreamento:", value=ped_up["codigo_rastreio"] or "")
                    
                    clientes_list = get_clientes()
                    cli_map = {c["id"]: c["nome"] for c in clientes_list}
                    cli_keys = list(cli_map.keys())
                    c_idx = cli_keys.index(ped_up["cliente_id"]) if ped_up["cliente_id"] in cli_keys else 0
                    u_cliente = st.selectbox("Cliente Associado:", options=cli_keys, format_func=lambda x: cli_map[x], index=c_idx)
                    
                col_b1, col_b2 = st.columns([7, 3])
                with col_b1:
                    sub_up = st.form_submit_button("🔄 Atualizar Pedido", use_container_width=True)
                with col_b2:
                    sub_del = st.form_submit_button("🗑️ Excluir Pedido", type="secondary", use_container_width=True)
                    
                if sub_up:
                    update_pedido(
                        pedido_id=sel_ped_up_id,
                        codigo_pedido=u_codigo,
                        cliente_id=u_cliente,
                        produto=u_produto,
                        quantidade=u_quantidade,
                        valor_total=u_valor,
                        status=u_status,
                        codigo_rastreio=u_rastreio
                    )
                    st.success("✅ Pedido atualizado com sucesso!")
                    st.rerun()
                    
                if sub_del:
                    delete_pedido(sel_ped_up_id)
                    st.warning("🗑️ Pedido removido do sistema!")
                    st.rerun()
    else:
        st.info("Nenhum pedido para atualizar.")
