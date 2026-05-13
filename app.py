import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
import hashlib

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="Financeiro Pro",
    layout="centered",
    page_icon="💰"
)

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.stApp{
    background: linear-gradient(135deg,#0f172a,#111827);
}

/* CARDS */

[data-testid="stMetric"]{

    background:rgba(17,24,39,0.95);
    border:1px solid rgba(255,255,255,0.08);
    padding:18px;
    border-radius:22px;
    box-shadow:0px 8px 25px rgba(0,0,0,0.35);
}

/* BOTÕES */

.stButton > button{

    width:100%;
    height:48px;
    border:none;
    border-radius:14px;
    background:linear-gradient(90deg,#2563eb,#3b82f6);
    color:white;
    font-weight:bold;
    transition:0.3s;
}

/* INPUTS */

.stTextInput input,
.stNumberInput input{

    background:#1e293b;
    color:white;
    border-radius:14px;
    border:1px solid #334155;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# FUNÇÕES
# =========================================================

def carregar_dados():

    modelo = {
        "saldo_conta": 0.0,
        "cdb_total": 0.0,
        "tesouro_total": 0.0,
        "gastos_diarios": [],
        "metas": []
    }

    if os.path.exists("dados.json"):

        try:

            with open("dados.json", "r") as f:

                dados = json.load(f)

                for k, v in modelo.items():

                    if k not in dados:
                        dados[k] = v

                return dados

        except:
            return modelo

    return modelo

def salvar_dados(dados):

    with open("dados.json", "w") as f:
        json.dump(dados, f, indent=4)

def formatar_br(valor):

    return f"R$ {float(valor):,.2f}"\
        .replace(",", "X")\
        .replace(".", ",")\
        .replace("X", ".")

# =========================================================
# DADOS
# =========================================================

dados = carregar_dados()

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# =========================================================
# LOGIN
# =========================================================

if not st.session_state.autenticado:

    st.title("🔐 Financeiro Pro")

    usuario = st.text_input("Usuário")

    senha = st.text_input(
        "Senha",
        type="password"
    )

    senha_correta = hashlib.sha256(
        "8708".encode()
    ).hexdigest()

    if st.button("Entrar"):

        senha_input = hashlib.sha256(
            senha.encode()
        ).hexdigest()

        if usuario == "giovanne" and senha_input == senha_correta:

            st.session_state.autenticado = True
            st.success("Login realizado!")
            st.rerun()

        else:
            st.error("Usuário ou senha incorretos")

    st.stop()

# =========================================================
# CÁLCULOS
# =========================================================

total_gastos = sum(
    g['valor']
    for g in dados['gastos_diarios']
)

total_investido = (
    dados['cdb_total'] +
    dados['tesouro_total']
)

saldo_livre = (
    dados['saldo_conta']
    - total_gastos
)

# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div style="
background:linear-gradient(135deg,#1e293b,#0f172a);
padding:28px;
border-radius:25px;
margin-bottom:20px;
border:1px solid rgba(255,255,255,0.08);
box-shadow:0px 8px 25px rgba(0,0,0,0.35);
">

<h1 style="margin:0;">
💰 Financeiro Pro
</h1>

<p style="margin-top:5px;color:#94a3b8;">
Seu controle financeiro inteligente
</p>

</div>
""", unsafe_allow_html=True)

# =========================================================
# DASHBOARD
# =========================================================

c1, c2 = st.columns(2)

c1.metric(
    "💳 Saldo em Conta",
    formatar_br(dados['saldo_conta'])
)

c2.metric(
    "💸 Livre",
    formatar_br(saldo_livre)
)

c3, c4 = st.columns(2)

c3.metric(
    "📈 Investido",
    formatar_br(total_investido)
)

c4.metric(
    "🧾 Gastos",
    formatar_br(total_gastos)
)

# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "💳 Conta",
    "💸 Gastos",
    "📈 Investimentos",
    "📊 Relatórios"
])

# =========================================================
# CONTA
# =========================================================

with tab1:

    saldo = st.number_input(
        "Saldo Atual",
        value=float(dados['saldo_conta']),
        format="%.2f"
    )

    if st.button("Salvar Saldo"):

        dados['saldo_conta'] = saldo

        salvar_dados(dados)

        st.success("Saldo atualizado!")

# =========================================================
# GASTOS
# =========================================================

with tab2:

    desc = st.text_input("Descrição")

    valor = st.number_input(
        "Valor",
        min_value=0.0,
        format="%.2f"
    )

    categoria = st.selectbox(
        "Categoria",
        [
            "Alimentação",
            "Transporte",
            "Lazer",
            "Saúde",
            "Casa",
            "Outros"
        ]
    )

    if st.button("Salvar Gasto"):

        if desc and valor > 0:

            dados['gastos_diarios'].append({

                "data":
                datetime.now().strftime("%d/%m %H:%M"),

                "desc": desc,
                "valor": valor,
                "cat": categoria
            })

            salvar_dados(dados)

            st.success("Gasto registrado!")

# =========================================================
# INVESTIMENTOS
# =========================================================

with tab3:

    st.subheader("🎯 Metas")

    nome_meta = st.text_input(
        "Nome da Meta"
    )

    valor_meta = st.number_input(
        "Valor da Meta",
        min_value=0.0
    )

    if st.button("Criar Meta"):

        dados['metas'].append({

            "nome": nome_meta,
            "alvo": valor_meta
        })

        salvar_dados(dados)

        st.success("Meta criada!")

    for meta in dados['metas']:

        alvo = meta['alvo']

        progresso = min(
            total_investido / alvo,
            1.0
        ) if alvo > 0 else 0

        porcentagem = progresso * 100

        falta = max(alvo - total_investido, 0)

        st.markdown(f"""
        <div style="
        background:#111827;
        padding:20px;
        border-radius:20px;
        margin-bottom:12px;
        border:1px solid rgba(255,255,255,0.08);
        ">

        <h2>
        🎯 {meta['nome']}
        </h2>

        <p>
        Meta: {formatar_br(alvo)}
        </p>

        <p style="color:#22c55e;">
        ✅ {porcentagem:.1f}% concluído
        </p>

        <p style="color:#facc15;">
        💰 Falta: {formatar_br(falta)}
        </p>

        </div>
        """, unsafe_allow_html=True)

        st.progress(progresso)

# =========================================================
# RELATÓRIOS
# =========================================================

with tab4:

    if dados['gastos_diarios']:

        df = pd.DataFrame(
            dados['gastos_diarios']
        )

        fig = px.pie(
            df,
            names='cat',
            values='valor',
            hole=0.65
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("⚙️ Configurações")

    if st.button("🚪 Sair"):

        st.session_state.autenticado = False
        st.rerun()
