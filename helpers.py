import streamlit as st
import pandas as pd
from datetime import datetime
import re

def apply_custom_css():
    """Aplica estilos CSS personalizados para uma interface moderna e profissional."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hero Header */
    .hero-container {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
    }
    
    .hero-title {
        color: #FFFFFF;
        font-size: 26px;
        font-weight: 700;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .hero-subtitle {
        color: #94A3B8;
        font-size: 14px;
        margin-bottom: 0px;
    }

    /* Cards e Containers */
    .metric-card {
        background-color: #ffffff;
        border-radius: 14px;
        padding: 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        text-align: center;
    }
    
    .badge-success { background-color: #DCFCE7; color: #15803D; }
    .badge-warning { background-color: #FEF3C7; color: #B45309; }
    .badge-danger { background-color: #FEE2E2; color: #B91C1C; }
    .badge-info { background-color: #E0E7FF; color: #4338CA; }
    .badge-primary { background-color: #DBEAFE; color: #1D4ED8; }
    .badge-secondary { background-color: #F1F5F9; color: #475569; }
    .badge-purple { background-color: #F3E8FF; color: #7E22CE; }

    /* Quick Action Buttons Container */
    .quick-action-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        transition: all 0.2s ease;
    }
    .quick-action-card:hover {
        background: #EFF6FF;
        border-color: #93C5FD;
    }

    /* Resposta IA Box */
    .ai-response-box {
        background: #F8FAFC;
        border-left: 4px solid #6366F1;
        padding: 18px;
        border-radius: 0 12px 12px 0;
        margin-top: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }

    /* Custom Table Wrapper */
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #E2E8F0;
    }
    </style>
    """, unsafe_allow_html=True)

def format_currency(val) -> str:
    """Formata valor numérico para Real brasileiro (R$ 1.234,56)."""
    try:
        val_float = float(val) if val is not None else 0.0
        return f"R$ {val_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "R$ 0,00"

def format_date(dt_str) -> str:
    """Formata string de data (ISO / SQLite) para formato amigável brasileiro."""
    if not dt_str:
        return "-"
    try:
        dt_str = str(dt_str).strip()
        if " " in dt_str:
            dt = datetime.strptime(dt_str.split(".")[0], "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%d/%m/%Y %H:%M")
        elif "-" in dt_str:
            dt = datetime.strptime(dt_str, "%Y-%m-%d")
            return dt.strftime("%d/%m/%Y")
        return dt_str
    except Exception:
        return str(dt_str)

def format_phone(phone_str) -> str:
    """Formata número de telefone para (XX) XXXXX-XXXX ou (XX) XXXX-XXXX."""
    if not phone_str:
        return "-"
    digits = re.sub(r"\D", "", str(phone_str))
    if len(digits) == 11:
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    elif len(digits) == 10:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    return str(phone_str)

def format_cpf(cpf_str) -> str:
    """Formata string para CPF (XXX.XXX.XXX-XX)."""
    if not cpf_str:
        return "-"
    digits = re.sub(r"\D", "", str(cpf_str))
    if len(digits) == 11:
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
    return str(cpf_str)

def format_cep(cep_str) -> str:
    """Formata string para CEP (XXXXX-XXX)."""
    if not cep_str:
        return "-"
    digits = re.sub(r"\D", "", str(cep_str))
    if len(digits) == 8:
        return f"{digits[:5]}-{digits[5:]}"
    return str(cep_str)

def render_badge(text: str, badge_type: str = "secondary") -> str:
    """Gera HTML de uma badge estilizada."""
    return f'<span class="badge badge-{badge_type}">{text}</span>'

def get_status_badge(status: str) -> str:
    """Retorna badge HTML correspondente ao status do pedido ou chamado."""
    if not status:
        return render_badge("Indefinido", "secondary")
    status_lower = str(status).lower().strip()
    
    mapping = {
        "entregue": "success",
        "resolvido": "success",
        "pago": "success",
        "fechado": "secondary",
        "enviado": "primary",
        "respondido": "info",
        "em análise": "warning",
        "em analise": "warning",
        "pendente": "warning",
        "aberto": "danger",
        "urgente": "danger",
        "cancelado": "danger",
        "extravio": "danger",
        "defeito": "danger",
    }
    
    badge_type = mapping.get(status_lower, "secondary")
    return render_badge(status, badge_type)

def get_priority_badge(priority: str) -> str:
    """Retorna badge HTML para prioridades."""
    if not priority:
        return render_badge("Normal", "secondary")
    p_lower = str(priority).lower().strip()
    if p_lower == "urgente":
        return render_badge("🚨 Urgente", "danger")
    elif p_lower == "alta":
        return render_badge("⚡ Alta", "danger")
    elif p_lower in ("média", "media"):
        return render_badge("⏳ Média", "warning")
    elif p_lower == "baixa":
        return render_badge("🟢 Baixa", "success")
    return render_badge(priority, "secondary")

def get_sentiment_badge(sentiment: str) -> str:
    """Retorna badge HTML para sentimento do cliente."""
    if not sentiment:
        return render_badge("Neutro", "secondary")
    s_lower = str(sentiment).lower().strip()
    if s_lower == "positivo":
        return render_badge("😊 Positivo", "success")
    elif s_lower == "neutro":
        return render_badge("😐 Neutro", "info")
    elif s_lower == "negativo":
        return render_badge("😠 Negativo", "warning")
    elif s_lower == "crítico" or s_lower == "critico":
        return render_badge("🔥 Crítico", "danger")
    return render_badge(sentiment, "secondary")

def export_to_csv(df: pd.DataFrame) -> bytes:
    """Converte DataFrame em bytes CSV codificado em UTF-8 com BOM para abrir perfeitamente no Excel."""
    return df.to_csv(index=False, sep=";", encoding="utf-8-sig").encode("utf-8-sig")
