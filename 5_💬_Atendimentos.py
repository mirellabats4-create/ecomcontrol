import streamlit as st
import pandas as pd
from database import (
    get_atendimentos, 
    get_atendimento_by_id, 
    add_atendimento, 
    update_atendimento, 
    delete_atendimento,
    get_clientes,
    get_pedidos
)
from utils.helpers import (
    apply_custom_css, 
    format_date, 
    get_status_badge, 
    get_sentiment_badge,
    export_to_csv
)
from services.ia_service import (
    gerar_resposta_atendimento, 
    analisar_sentimento_urgencia
)

st.set_page_config(page_title="Atendimentos • EcomControl", page_icon="💬", layout="wide")
apply_custom_css()

st.markdown("""
<div class="hero-container">
    <div class="hero-title">💬 Central de Atendimento & SAC Multicanal</div>
    <div class="hero-subtitle">Gestão de tickets de WhatsApp, Mercado Livre, Shopee, Chat e E-mail com respostas inteligentes por IA.</div>
</div>
""", unsafe_allow_html=True)

tab_fila, tab_novo, tab_responder = st.tabs(["📥 Fila de Atendimentos", "➕ Novo Ticket de SAC", "✍️ Responder Ticket"])

# ==========================================
# ABA 1: FILA DE ATENDIMENTOS
# ==========================================
with tab_fila:
    c1, c2, c3, c4 = st.columns([3, 3, 4, 2])
    with c1:
        f_status = st.selectbox("Status:", ["Todos", "Pendente", "Respondido", "Fechado"])
    with c2:
        f_canal = st.selectbox("Canal:", ["Todos", "WhatsApp", "Mercado Livre", "Shopee", "Email", "Chat", "Telefone"])
    with c3:
        f_search = st.text_input("🔍 Pesquisar:", placeholder="Cliente, pedido ou assunto...")
    with c4:
        st.markdown("<br>", unsafe_allow_html=True)
        atends_filtrados = get_atendimentos(
            status=f_status if f_status != "Todos" else None,
            canal=f_canal if f_canal != "Todos" else None,
            search=f_search if f_search else None
        )
        if atends_filtrados:
            st.download_button("📥 Exportar", data=export_to_csv(pd.DataFrame(atends_filtrados)), file_name="atendimentos.csv", use_container_width=True)

    st.markdown(f"**Tickets encontrados:** `{len(atends_filtrados)}`")
    
    if atends_filtrados:
        data_view = []
        for a in atends_filtrados:
            data_view.append({
                "ID": f"#{a['id']}",
                "Cliente": a["cliente_nome"],
                "Canal": a["canal"],
                "Assunto": a["assunto"],
                "Pedido": a.get("codigo_pedido") or "-",
                "Sentimento": a["sentimento"],
                "Status": a["status"],
                "Data": format_date(a["criado_em"])
            })
        st.dataframe(pd.DataFrame(data_view), use_container_width=True, hide_index=True)
        
        st.divider()
        st.markdown("### 👁️ **Visualização do Ticket & Histórico**")
        atend_map = {a["id"]: f"#{a['id']} - {a['cliente_nome']} ({a['canal']}: {a['assunto']}) [{a['status']}]" for a in atends_filtrados}
        sel_at_id = st.selectbox("Selecione o ticket para visualizar:", options=list(atend_map.keys()), format_func=lambda x: atend_map[x])
        
        if sel_at_id:
            at_detalhe = get_atendimento_by_id(sel_at_id)
            c_msg1, c_msg2 = st.columns([6, 4])
            with c_msg1:
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin:0 0 8px 0; color:#1E293B;">📨 Mensagem do Cliente</h4>
                    <p style="margin:4px 0;"><strong>Canal:</strong> {at_detalhe['canal']} &nbsp; <strong>Sentimento:</strong> {get_sentiment_badge(at_detalhe['sentimento'])}</p>
                    <p style="margin:4px 0;"><strong>Assunto:</strong> {at_detalhe['assunto']}</p>
                    <div style="background:#F1F5F9; padding:12px; border-radius:8px; margin-top:8px; font-size:14px; color:#1E293B;">
                        "{at_detalhe['mensagem_cliente']}"
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if at_detalhe.get('resposta_enviada'):
                    st.markdown(f"""
                    <div class="metric-card" style="margin-top:15px; border-left: 4px solid #10B981;">
                        <h4 style="margin:0 0 8px 0; color:#10B981;">✅ Resposta Enviada ao Cliente</h4>
                        <div style="background:#F8FAFC; padding:12px; border-radius:8px; font-size:14px; color:#1E293B;">
                            {at_detalhe['resposta_enviada']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("⚠️ Este ticket ainda não possui resposta cadastrada.")
            
            with c_msg2:
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin:0 0 8px 0; color:#1E293B;">👤 Contato & Pedido</h4>
                    <p style="margin:4px 0;"><strong>Cliente:</strong> {at_detalhe['cliente_nome']}</p>
                    <p style="margin:4px 0;"><strong>E-mail:</strong> {at_detalhe['cliente_email']}</p>
                    <p style="margin:4px 0;"><strong>Telefone:</strong> {at_detalhe['cliente_telefone'] or '-'}</p>
                    <p style="margin:4px 0;"><strong>Pedido:</strong> {at_detalhe.get('codigo_pedido') or 'N/A'}</p>
                    <p style="margin:4px 0;"><strong>Produto:</strong> {at_detalhe.get('pedido_produto') or '-'}</p>
                    <p style="margin:4px 0;"><strong>Rastreio:</strong> {at_detalhe.get('codigo_rastreio') or '-'}</p>
                    <p style="margin:4px 0;"><strong>Criado em:</strong> {format_date(at_detalhe['criado_em'])}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Nenhum ticket encontrado com os filtros selecionados.")

# ==========================================
# ABA 2: NOVO TICKET
# ==========================================
with tab_novo:
    st.markdown("### ➕ **Registrar Novo Ticket de SAC**")
    clientes = get_clientes()
    pedidos = get_pedidos()
    
    if not clientes:
        st.warning("Cadastre clientes para registrar atendimentos.")
    else:
        with st.form("form_novo_atendimento", clear_on_submit=True):
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                cli_dict = {c["id"]: f"{c['nome']} ({c['email']})" for c in clientes}
                sel_cli_id = st.selectbox("Cliente: *", options=list(cli_dict.keys()), format_func=lambda x: cli_dict[x])
                
                ped_dict = {0: "Nenhum pedido vinculado"}
                for p in pedidos:
                    ped_dict[p["id"]] = f"{p['codigo_pedido']} - {p['produto']}"
                sel_ped_id = st.selectbox("Pedido (Opcional):", options=list(ped_dict.keys()), format_func=lambda x: ped_dict[x])
                
                canal = st.selectbox("Canal de Atendimento:", ["WhatsApp", "Mercado Livre", "Shopee", "Email", "Chat", "Telefone"])
                assunto = st.text_input("Assunto / Tópico: *", placeholder="Ex: Dúvida sobre rastreamento")
                
            with col_t2:
                sentimento = st.selectbox("Sentimento Inicial:", ["Neutro", "Positivo", "Negativo", "Crítico"])
                status_ini = st.selectbox("Status:", ["Pendente", "Respondido", "Fechado"])
                mensagem = st.text_area("Mensagem Enviada pelo Cliente: *", placeholder="Cole aqui a mensagem do WhatsApp, ML, Shopee...", height=120)
                
            sub_atend = st.form_submit_button("💾 Salvar Atendimento", use_container_width=True)
            
            if sub_atend:
                if not assunto or not mensagem:
                    st.error("Assunto e Mensagem são obrigatórios!")
                else:
                    novo_id = add_atendimento(
                        cliente_id=sel_cli_id,
                        pedido_id=sel_ped_id if sel_ped_id != 0 else None,
                        canal=canal,
                        assunto=assunto,
                        mensagem_cliente=mensagem,
                        status=status_ini,
                        sentimento=sentimento
                    )
                    st.success(f"🎉 Ticket #{novo_id} registrado com sucesso!")
                    st.rerun()

# ==========================================
# ABA 3: RESPONDER TICKET COM IA
# ==========================================
with tab_responder:
    st.markdown("### ✍️ **Responder Ticket & Assistência por IA**")
    todos_atends = get_atendimentos()
    
    if todos_atends:
        dict_resp = {a["id"]: f"#{a['id']} - {a['cliente_nome']} ({a['canal']}: {a['assunto']}) [{a['status']}]" for a in todos_atends}
        sel_resp_id = st.selectbox("Selecione o ticket para responder:", options=list(dict_resp.keys()), format_func=lambda x: dict_resp[x], key="sel_resp_box")
        
        at_resp = get_atendimento_by_id(sel_resp_id)
        if at_resp:
            st.markdown(f"""
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:15px; border-radius:10px; margin-bottom:15px;">
                <strong>Cliente:</strong> {at_resp['cliente_nome']} &nbsp;|&nbsp; 
                <strong>Canal:</strong> {at_resp['canal']} &nbsp;|&nbsp; 
                <strong>Pedido:</strong> {at_resp.get('codigo_pedido') or 'N/A'}<br>
                <div style="margin-top:8px; font-style:italic; color:#334155;">"{at_resp['mensagem_cliente']}"</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Botão para gerar com IA
            col_ia1, col_ia2 = st.columns([6, 4])
            with col_ia1:
                tom_escolhido = st.selectbox("Tom da Resposta da IA:", [
                    "Empático e Resolutivo (Padrão SAC)",
                    "Formal e Institucional",
                    "Rápido, Direto e Objetivo",
                    "Acolhedor para Clientes Insatisfeitos"
                ])
            with col_ia2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🤖 Gerar Sugestão de Resposta com Gemini", use_container_width=True):
                    with st.spinner("Consultando Gemini IA..."):
                        sugestao = gerar_resposta_atendimento(
                            cliente_nome=at_resp['cliente_nome'],
                            pedido_codigo=at_resp.get('codigo_pedido'),
                            produto=at_resp.get('pedido_produto'),
                            mensagem_cliente=at_resp['mensagem_cliente'],
                            tom=tom_escolhido
                        )
                        st.session_state[f"resp_draft_{sel_resp_id}"] = sugestao
                        st.success("Sugestão gerada com sucesso!")
            
            # Área de Edição e Envio da Resposta
            texto_inicial = st.session_state.get(f"resp_draft_{sel_resp_id}", at_resp.get("resposta_enviada") or "")
            
            with st.form("form_enviar_resposta"):
                resposta_final = st.text_area("Texto da Resposta:", value=texto_inicial, height=180)
                col_st1, col_st2 = st.columns(2)
                with col_st1:
                    novo_st = st.selectbox("Atualizar Status para:", ["Respondido", "Fechado", "Pendente"], index=0)
                with col_st2:
                    sentimentos_opts = ["Positivo", "Neutro", "Negativo", "Crítico"]
                    s_idx = sentimentos_opts.index(at_resp["sentimento"]) if at_resp["sentimento"] in sentimentos_opts else 1
                    novo_sent = st.selectbox("Sentimento do Cliente:", sentimentos_opts, index=s_idx)
                    
                sub_envio = st.form_submit_button("💾 Salvar Resposta do Atendimento", use_container_width=True)
                
                if sub_envio:
                    update_atendimento(
                        atendimento_id=sel_resp_id,
                        canal=at_resp["canal"],
                        assunto=at_resp["assunto"],
                        mensagem_cliente=at_resp["mensagem_cliente"],
                        resposta_enviada=resposta_final,
                        status=novo_st,
                        sentimento=novo_sent,
                        pedido_id=at_resp.get("pedido_id")
                    )
                    st.success("🎉 Resposta gravada com sucesso no ticket!")
                    st.rerun()
    else:
        st.info("Nenhum ticket disponível para responder.")
