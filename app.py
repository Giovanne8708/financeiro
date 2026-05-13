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
# CSS PREMIUM
# =========================================================

st.markdown("""
<style>

.stApp{
    background: linear-gradient(135deg,#0f172a,#111827);
    color:white;
}

/* CARDS */

[data-testid="stMetric"]{
    background: rgba(17,24,39,0.95);
    border:1px solid rgba(255,255,255,0.08);
    padding:18px;
    border-radius:22px;
    box-shadow:0px 8px 25px rgba(0,0,0,0.35);
}

/* BOTÕES */

.stButton > button{
    width:100%;
    height:50px;
    border:none;
    border-radius:14px;
    background:linear-gradient(90deg,#2563eb,#3b82f6);
    color:white;
    font-weight:bold;
    font-size:16px;
}

/* INPUTS */

.stTextInput input,
.stNumberInput input{
    background:#1e293b;
    color:white;
    border-radius:14px;
    border:1px solid #334155;
}

/* SELECT */

.stSelectbox div[data-baseweb="select"]{
    background:#1e293b;
    border-radius:14px;
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

    st.markdown("""
    <div style="
    background:#111827;
    padding:35px;
    border-radius:25px;
    margin-top:80px;
    border:1px solid rgba(255,255,255,0.08);
    text-align:center;
    ">
    <h1>🔐 Financeiro Pro</h1>
    <p style="color:gray;">
    Faça login para continuar
    </p>
    </div>
    """, unsafe_allow_html=True)

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

<p style="
margin-top:5px;
color:#94a3b8;
">
Seu controle financeiro inteligente
</p>

</div>
""", unsafe_allow_html=True)

# =========================================================
# DASHBOARD
# =========================================================

c1, c2 = st.columns(2)

c1.metric(
    "💳 Saldo",
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

    st.subheader("💳 Saldo Bancário")

    saldo = st.number_input(
        "Saldo Atual",
        value=float(dados['saldo_conta']),
        format="%.2f"
    )

    if st.button("Salvar Saldo"):

        dados['saldo_conta'] = saldo

        salvar_dados(dados)

        st.toast("✅ Saldo atualizado!")

# =========================================================
# GASTOS
# =========================================================

with tab2:

    st.subheader("💸 Registrar Gasto")

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

            st.toast("✅ Gasto registrado!")

    st.divider()

    st.subheader("🧾 Últimos Gastos")

    ultimos = dados['gastos_diarios'][-5:][::-1]

    for g in ultimos:

        st.markdown(f"""
        <div style="
        background:#111827;
        padding:18px;
        border-radius:18px;
        margin-bottom:10px;
        border-left:5px solid #ef4444;
        ">

        <h4 style="margin:0;">
        {g['desc']}
        </h4>

        <p style="color:gray;margin:0;">
        {g['cat']}
        </p>

        <h3 style="margin-top:8px;">
        {formatar_br(g['valor'])}
        </h3>

        </div>
        """, unsafe_allow_html=True)

# =========================================================
# INVESTIMENTOS
# =========================================================

with tab3:

    st.subheader("📈 Carteira")

    i1, i2, i3 = st.columns(3)

    i1.metric(
        "CDB",
        formatar_br(dados['cdb_total'])
    )

    i2.metric(
        "Tesouro",
        formatar_br(dados['tesouro_total'])
    )

    i3.metric(
        "Total",
        formatar_br(total_investido)
    )

    st.divider()

    st.subheader("💵 Aplicar Investimento")

    valor_inv = st.number_input(
        "Valor para investir",
        min_value=0.0,
        format="%.2f"
    )

    tipo = st.selectbox(
        "Tipo",
        [
            "CDB",
            "Tesouro"
        ]
    )

    if st.button("Aplicar"):

        if valor_inv > 0:

            if tipo == "CDB":
                dados['cdb_total'] += valor_inv
            else:
                dados['tesouro_total'] += valor_inv

            dados['saldo_conta'] -= valor_inv

            salvar_dados(dados)

            st.toast("📈 Investimento realizado!")

    st.divider()

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

        st.toast("🎯 Meta criada!")

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
# RELATÓRIOS PRO
# =========================================================

with tab4:

    st.subheader("📊 Central Inteligente")

    if dados['gastos_diarios']:

        df = pd.DataFrame(dados['gastos_diarios'])

        total_mes = df['valor'].sum()

        media_gastos = df['valor'].mean()

        maior_gasto = df['valor'].max()

        qtd_gastos = len(df)

        # =========================
        # MÉTRICAS
        # =========================

        a1, a2 = st.columns(2)

        a1.metric(
            "💸 Total Gasto",
            formatar_br(total_mes)
        )

        a2.metric(
            "📊 Média",
            formatar_br(media_gastos)
        )

        a3, a4 = st.columns(2)

        a3.metric(
            "🔥 Maior Gasto",
            formatar_br(maior_gasto)
        )

        a4.metric(
            "🧾 Registros",
            qtd_gastos
        )

        st.divider()

        # =========================
        # GRÁFICO BARRAS
        # =========================

        st.subheader("📈 Gastos por Categoria")

        categoria_df = df.groupby(
            'cat'
        )['valor'].sum().reset_index()

        fig = px.bar(
            categoria_df,
            x='cat',
            y='valor',
            text_auto=True,
            title='Distribuição de Gastos'
        )

        fig.update_layout(
            paper_bgcolor='#0f172a',
            plot_bgcolor='#0f172a',
            font_color='white'
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # =========================
        # LINHA DO TEMPO
        # =========================

        st.subheader("📊 Evolução dos Gastos")

        try:

            df['ordem'] = range(len(df))

            fig2 = px.line(
                df,
                x='ordem',
                y='valor',
                markers=True,
                title='Linha do Tempo'
            )

            fig2.update_layout(
                paper_bgcolor='#0f172a',
                plot_bgcolor='#0f172a',
                font_color='white'
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

        except:
            pass

        # =========================
        # ÚLTIMOS MOVIMENTOS
        # =========================

        st.subheader("🧾 Últimos Movimentos")

        ultimos = df.tail(5).iloc[::-1]

        for _, g in ultimos.iterrows():

            st.markdown(f"""
            <div style="
            background:#111827;
            padding:18px;
            border-radius:18px;
            margin-bottom:10px;
            border-left:5px solid #3b82f6;
            ">

            <h4 style="margin:0;">
            {g['desc']}
            </h4>

            <p style="margin:0;color:gray;">
            {g['cat']}
            </p>

            <h3 style="margin-top:8px;">
            {formatar_br(g['valor'])}
            </h3>

            </div>
            """, unsafe_allow_html=True)

    else:

        st.info("Nenhum gasto registrado ainda.")

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("⚙️ Configurações")

    if st.button("🚪 Sair"):

        st.session_state.autenticado = False
        st.rerun()

    st.divider()

    st.subheader("🗑️ Reset")

    if st.button("Resetar Tudo"):

        dados = {

            "saldo_conta": 0.0,
            "cdb_total": 0.0,
            "tesouro_total": 0.0,
            "gastos_diarios": [],
            "metas": []
        }

        salvar_dados(dados)

        st.warning("Tudo resetado!")
