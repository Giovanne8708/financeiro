import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
import hashlib
import time

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="Financeiro Pro",
    layout="wide",
    page_icon="💰"
)

# =========================================================
# CSS PREMIUM
# =========================================================

st.markdown("""
<style>

.stApp {
    background:
    radial-gradient(circle at top left, #1e293b, #0f172a);
    color: white;
}

/* METRICS */

[data-testid="stMetric"] {

    background: rgba(30,41,59,0.75);

    border: 1px solid rgba(255,255,255,0.08);

    padding: 20px;

    border-radius: 22px;

    box-shadow:
    0px 8px 25px rgba(0,0,0,0.35);

    backdrop-filter: blur(10px);
}

/* BOTÕES */

.stButton > button {

    width:100%;

    border:none;

    border-radius:14px;

    height:50px;

    background:
    linear-gradient(90deg,#2563eb,#3b82f6);

    color:white;

    font-weight:bold;

    transition:0.3s;
}

.stButton > button:hover {

    transform:translateY(-2px);

    box-shadow:
    0 8px 20px rgba(37,99,235,0.4);
}

/* INPUTS */

.stTextInput input,
.stNumberInput input {

    background:#1e293b;

    color:white;

    border-radius:12px;

    border:1px solid #334155;
}

/* TABS */

.stTabs [data-baseweb="tab"] {

    font-size:16px;

    padding:12px;

    border-radius:12px;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {

    background:#111827;

    border-right:
    1px solid rgba(255,255,255,0.08);
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# FUNÇÕES
# =========================================================

def carregar_dados():

    modelo = {
        "cdb_total": 0.0,
        "tesouro_total": 0.0,
        "gastos_diarios": [],
        "contas_fixas": [],
        "metas": [],
        "salario": 0.0,
        "extra": 0.0,
        "pct_invest": 10.0
    }

    if os.path.exists("dados.json"):

        try:

            with open("dados.json", "r") as f:

                d = json.load(f)

                for k, v in modelo.items():

                    if k not in d:
                        d[k] = v

                return d

        except:
            return modelo

    return modelo

def salvar_dados(dados):

    with open("dados.json", "w") as f:
        json.dump(dados, f, indent=4)

def formatar_br(valor):

    return f"R$ {float(valor):,.2f}"\
        .replace(',', 'X')\
        .replace('.', ',')\
        .replace('X', '.')

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
    max-width:450px;
    margin:auto;
    margin-top:100px;
    padding:35px;
    background:#111827;
    border-radius:25px;
    border:1px solid rgba(255,255,255,0.08);
    ">
    <h1 style="text-align:center;">
    🔐 Financeiro Pro
    </h1>
    <p style="text-align:center;color:gray;">
    Acesse sua central financeira
    </p>
    </div>
    """, unsafe_allow_html=True)

    u = st.text_input("Usuário")
    s = st.text_input("Senha", type="password")

    senha_correta = hashlib.sha256(
        "8708".encode()
    ).hexdigest()

    if st.button("Entrar"):

        senha_input = hashlib.sha256(
            s.encode()
        ).hexdigest()

        if u == "giovanne" and senha_input == senha_correta:

            st.session_state.autenticado = True

            st.toast("Login realizado!", icon="✅")

            st.rerun()

        else:
            st.error("Usuário ou senha incorretos")

    st.stop()

# =========================================================
# CÁLCULOS
# =========================================================

total_gastos = sum(
    g.get('valor', 0)
    for g in dados['gastos_diarios']
)

receita_total = (
    dados['salario'] +
    dados['extra']
)

saldo_livre = receita_total - total_gastos

total_investido = (
    dados['cdb_total'] +
    dados['tesouro_total']
)

media_gastos = total_gastos / max(
    len(dados['gastos_diarios']),
    1
)

dias_restantes = 15

previsao = saldo_livre - (
    media_gastos * dias_restantes
)

# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div style="
background:
linear-gradient(135deg,#1e293b,#0f172a);

padding:30px;

border-radius:25px;

margin-bottom:25px;

border:1px solid rgba(255,255,255,0.08);

box-shadow:
0 8px 25px rgba(0,0,0,0.35);
">

<h1 style="margin:0;">
💰 Financeiro Pro
</h1>

<p style="
color:#94a3b8;
margin-top:5px;
">
Controle inteligente das suas finanças
</p>

</div>
""", unsafe_allow_html=True)

# =========================================================
# METRICS
# =========================================================

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "💰 Saldo Livre",
        formatar_br(saldo_livre)
    )

with c2:
    st.metric(
        "📈 Investido",
        formatar_br(total_investido)
    )

with c3:
    st.metric(
        "💸 Gastos",
        formatar_br(total_gastos)
    )

# =========================================================
# PREVISÃO
# =========================================================

if previsao < 0:

    st.error(
        f"⚠️ Previsão negativa em 15 dias: "
        f"{formatar_br(previsao)}"
    )

else:

    st.success(
        f"📊 Previsão positiva para 15 dias: "
        f"{formatar_br(previsao)}"
    )

# =========================================================
# AÇÕES RÁPIDAS
# =========================================================

st.subheader("⚡ Ações Rápidas")

a1, a2, a3 = st.columns(3)

with a1:

    if st.button("💸 Novo Gasto"):
        st.toast("Use a aba Fluxo")

with a2:

    if st.button("📈 Investir"):
        st.toast("Use a aba Investimentos")

with a3:

    if st.button("🎯 Nova Meta"):
        st.toast("Use a aba Metas")

# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "💰 Fluxo",
    "🎯 Investimentos",
    "📝 Parcelas",
    "📊 Relatórios"
])

# =========================================================
# TAB FLUXO
# =========================================================

with tab1:

    st.subheader("📥 Receitas")

    r1, r2 = st.columns(2)

    salario = r1.number_input(
        "Salário",
        value=float(dados['salario']),
        format="%.2f"
    )

    extra = r2.number_input(
        "Extras",
        value=float(dados['extra']),
        format="%.2f"
    )

    if st.button("Salvar Receitas"):

        dados['salario'] = salario
        dados['extra'] = extra

        salvar_dados(dados)

        st.success("Receitas atualizadas!")

        st.rerun()

    st.divider()

    st.subheader("💸 Registrar Gasto")

    g_n = st.text_input("Descrição")

    g_v = st.number_input(
        "Valor",
        min_value=0.0,
        format="%.2f"
    )

    g_c = st.selectbox(
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

        if g_n and g_v > 0:

            dados['gastos_diarios'].append({

                "data":
                datetime.now().strftime("%d/%m %H:%M"),

                "desc": g_n,

                "valor": g_v,

                "cat": g_c
            })

            salvar_dados(dados)

            st.toast("Gasto salvo!", icon="✅")

            st.rerun()

# =========================================================
# TAB INVESTIMENTOS
# =========================================================

with tab2:

    st.subheader("📈 Aplicar Investimento")

    v_pct = st.slider(
        "Porcentagem da Receita",
        0,
        100,
        int(dados['pct_invest'])
    )

    valor_aplicar = (
        receita_total *
        (v_pct / 100)
    ) / 2

    st.info(
        f"Valor sugerido: "
        f"{formatar_br(valor_aplicar)}"
    )

    i1, i2 = st.columns(2)

    with i1:

        if st.button("Aplicar em CDB"):

            dados['cdb_total'] += valor_aplicar

            dados['gastos_diarios'].append({

                "data":
                datetime.now().strftime("%d/%m"),

                "desc": "Aplicação CDB",

                "valor": valor_aplicar,

                "cat": "Investimento"
            })

            salvar_dados(dados)

            st.success("Aplicado no CDB!")

            st.rerun()

    with i2:

        if st.button("Aplicar Tesouro"):

            dados['tesouro_total'] += valor_aplicar

            dados['gastos_diarios'].append({

                "data":
                datetime.now().strftime("%d/%m"),

                "desc": "Aplicação Tesouro",

                "valor": valor_aplicar,

                "cat": "Investimento"
            })

            salvar_dados(dados)

            st.success("Aplicado no Tesouro!")

            st.rerun()

    st.divider()

    st.subheader("🎯 Metas")

    m_n = st.text_input("Nome da Meta")

    m_v = st.number_input(
        "Valor da Meta",
        min_value=0.0
    )

    if st.button("Criar Meta"):

        dados['metas'].append({

            "nome": m_n,

            "alvo": m_v
        })

        salvar_dados(dados)

        st.success("Meta criada!")

        st.rerun()

    for i, m in enumerate(dados['metas']):

        progresso = min(
            total_investido / m['alvo'],
            1.0
        )

        st.markdown(f"""
        <div style="
        background:#111827;
        padding:20px;
        border-radius:20px;
        margin-bottom:15px;
        ">
        <h3>{m['nome']}</h3>
        <p>
        Meta:
        {formatar_br(m['alvo'])}
        </p>
        </div>
        """, unsafe_allow_html=True)

        st.progress(progresso)

# =========================================================
# TAB PARCELAS
# =========================================================

with tab3:

    st.subheader("📝 Parcelamentos")

    nome_parc = st.text_input("Nome")

    valor_parc = st.number_input(
        "Valor Parcela",
        min_value=0.0
    )

    total_parc = st.number_input(
        "Qtd Parcelas",
        1,
        100
    )

    if st.button("Adicionar Parcela"):

        dados['contas_fixas'].append({

            "nome": nome_parc,

            "valor": valor_parc,

            "atual": 1,

            "total": total_parc
        })

        salvar_dados(dados)

        st.success("Parcela adicionada!")

        st.rerun()

    for c in dados['contas_fixas']:

        st.markdown(f"""
        <div style="
        background:#111827;
        padding:18px;
        border-radius:18px;
        margin-bottom:12px;
        ">
        <h4>{c['nome']}</h4>
        <p>
        {c['atual']} / {c['total']}
        </p>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# TAB RELATÓRIOS
# =========================================================

with tab4:

    st.subheader("📊 Relatórios")

    if dados['gastos_diarios']:

        with st.spinner(
            "Carregando relatórios..."
        ):
            time.sleep(1)

        df = pd.DataFrame(
            dados['gastos_diarios']
        )

        filtro = st.selectbox(
            "Categoria",
            ["Todos"] +
            list(df['cat'].unique())
        )

        if filtro != "Todos":

            df = df[
                df['cat'] == filtro
            ]

        # DONUT

        fig = px.pie(

            df,

            names='cat',

            values='valor',

            hole=0.65,

            title="Distribuição de Gastos"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # LINHA

        try:

            df['mes'] = pd.to_datetime(

                df['data'],

                format='%d/%m %H:%M',

                errors='coerce'

            ).dt.strftime('%m/%Y')

            graf_mes = df.groupby(
                'mes'
            )['valor'].sum().reset_index()

            fig2 = px.line(

                graf_mes,

                x='mes',

                y='valor',

                markers=True,

                title='📈 Evolução dos Gastos'
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

        except:
            pass

        # INSIGHTS

        st.subheader(
            "🤖 Resumo Inteligente"
        )

        categoria_top = df.groupby(
            'cat'
        )['valor'].sum().idxmax()

        valor_top = df.groupby(
            'cat'
        )['valor'].sum().max()

        st.info(f"""

Maior categoria:
{categoria_top}

Maior gasto:
{formatar_br(valor_top)}

Média por lançamento:
{formatar_br(df['valor'].mean())}

Total movimentado:
{formatar_br(df['valor'].sum())}

""")

        # EXTRATO

        st.subheader(
            "🧾 Últimos Lançamentos"
        )

        df_display = df.tail(10)[::-1]

        for i, row in df_display.iterrows():

            cor = "#ef4444"

            if row['cat'] == "Investimento":
                cor = "#3b82f6"

            st.markdown(f"""
            <div style="
            background:#161b22;

            padding:18px;

            border-radius:18px;

            margin-bottom:12px;

            border-left:
            6px solid {cor};
            ">

            <div style="
            display:flex;

            justify-content:space-between;

            align-items:center;
            ">

            <div>

            <h4 style="margin:0;">
            {row['desc']}
            </h4>

            <p style="
            margin:0;
            color:gray;
            ">
            {row['cat']}
            </p>

            </div>

            <div>

            <h3 style="margin:0;">
            {formatar_br(row['valor'])}
            </h3>

            </div>

            </div>

            </div>
            """, unsafe_allow_html=True)

        # DOWNLOAD

        csv = df.to_csv(
            index=False
        ).encode('utf-8')

        st.download_button(

            "📥 Baixar Extrato",

            csv,

            "extrato.csv",

            "text/csv"
        )

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("⚙️ Configurações")

    if st.button("🚪 Sair"):

        st.session_state.autenticado = False

        st.rerun()

    st.divider()

    if st.checkbox(
        "Habilitar Reset"
    ):

        if st.button(
            "🗑️ Zerar Quinzena"
        ):

            dados[
                "gastos_diarios"
            ] = []

            salvar_dados(dados)

            st.warning(
                "Dados resetados!"
            )

            st.rerun()
