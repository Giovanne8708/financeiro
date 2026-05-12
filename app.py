import streamlit as st
import json
import os
import pandas as pd

# --- CONFIGURAÇÕES DO APP ---
st.set_page_config(page_title="Financeiro Pro", layout="centered", page_icon="📈")

# --- ESTILO CSS PARA DESIGN MODERNO ---
st.markdown("""
    <style>
    /* Fundo e Container Principal */
    .main { background-color: #0d1117; }
    
    /* Estilização dos Cards */
    .st-emotion-cache-1r6slb0 { border-radius: 15px; border: 1px solid #30363d; padding: 20px; background-color: #161b22; }
    
    /* Títulos e Métricas */
    h1, h2, h3 { font-family: 'Inter', sans-serif; color: #58a6ff !important; font-weight: 700; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem !important; color: #ffffff !important; }
    
    /* Botões Modernos */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background-color: #238636;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #2ea043; border: none; color: white; }
    
    /* Card de Conta Individual */
    .conta-card {
        background-color: #0d1117;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS ---
def carregar_dados():
    modelo = {"patrimonio": 0.0, "gastos_diarios": [], "contas_fixas": [], "salario": 0.0, "extra": 0.0, "pct": 10.0, "quinzena": "1ª Quinzena"}
    if os.path.exists("dados.json"):
        try:
            with open("dados.json", "r") as f:
                d = json.load(f)
                for k, v in modelo.items():
                    if k not in d: d[k] = v
                return d
        except:
            return modelo
    return modelo

def salvar_dados(dados):
    with open("dados.json", "w") as f:
        json.dump(dados, f, indent=4)

def formatar_br(valor):
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# --- INICIALIZAÇÃO ---
dados = carregar_dados()

# --- LOGIN SIMPLES ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>🔐 Financeiro</h1>", unsafe_allow_html=True)
    with st.container(border=True):
        u = st.text_input("Usuário")
        s = st.text_input("Senha", type="password")
        if st.button("Acessar Sistema"):
            if u == "giovanne" and s == "8708":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Credenciais inválidas")
    st.stop()

# --- CONTEÚDO PRINCIPAL ---
st.markdown("<h1 style='text-align: center;'>📱 Meu Financeiro</h1>", unsafe_allow_html=True)

# Resumo de Saldo em destaque
total_gastos = sum(g['valor'] for g in dados['gastos_diarios'])
saldo_livre = (dados['salario'] + dados['extra']) - total_gastos
aporte = ((dados['salario'] + dados['extra']) * (dados['pct'] / 100)) / 2

col_m1, col_m2 = st.columns(2)
with col_m1:
    st.metric("Saldo Disponível", formatar_br(saldo_livre))
with col_m2:
    st.metric("Investimento Sugerido", formatar_br(aporte))

st.divider()

# Abas Modernas
tab1, tab2, tab3 = st.tabs(["💰 Fluxo Atual", "📝 Contas/Parcelas", "📊 Relatório"])

with tab1:
    with st.container(border=True):
        st.subheader("📥 Entradas da Quinzena")
        c1, c2, c3 = st.columns(3)
        v_sal = c1.number_input("Salário", value=float(dados['salario']), format="%.2f")
        v_ext = c2.number_input("Extras", value=float(dados['extra']), format="%.2f")
        v_pct = c3.number_input("Meta %", value=float(dados['pct']), format="%.1f")
        
        if (v_sal != dados['salario'] or v_ext != dados['extra'] or v_pct != dados['pct']):
            dados.update({"salario": v_sal, "extra": v_ext, "pct": v_pct})
            salvar_dados(dados)
            st.rerun()

    st.write("")
    with st.container(border=True):
        st.subheader("🛒 Novo Gasto")
        g_n = st.text_input("O que comprou?", placeholder="Ex: Mercado, Posto...")
        g_v = st.number_input("Valor R$", min_value=0.0, format="%.2f", key="gasto_v")
        g_c = st.selectbox("Categoria", ["Alimentação", "Transporte", "Lazer", "Saúde", "Casa", "Outros"])
        if st.button("Registrar Gasto"):
            if g_n and g_v > 0:
                dados['gastos_diarios'].append({"desc": g_n, "valor": g_v, "cat": g_c})
                salvar_dados(dados)
                st.toast(f"Gasto de {formatar_br(g_v)} salvo!")
                st.rerun()

with tab2:
    st.subheader("📅 Gestão de Parcelas")
    
    with st.expander("+ Adicionar Conta Parcelada"):
        nc = st.text_input("Nome do Item", placeholder="Ex: iPhone, Notebook...")
        vc = st.number_input("Valor da Parcela R$", min_value=0.0, format="%.2f")
        cp1, cp2 = st.columns(2)
        p_at = cp1.number_input("Parc. Atual", 1, 100, 1)
        p_to = cp2.number_input("Total Parc.", 1, 100, 1)
        if st.button("Cadastrar Conta"):
            if nc and vc > 0:
                dados['contas_fixas'].append({"nome": nc, "valor": vc, "atual": p_at, "total": p_to})
                salvar_dados(dados)
                st.rerun()

    st.write("")
    # Listagem de contas com design de card
    for i, c in enumerate(dados['contas_fixas']):
        with st.container(border=True):
            col_a, col_b = st.columns([3, 1])
            col_a.markdown(f"### {c['nome']}")
            col_b.markdown(f"**{formatar_br(c['valor'])}**")
            
            # Barra de progresso da parcela
            progresso = c['atual'] / c['total']
            st.progress(progresso)
            st.caption(f"Progresso: Parcela {c['atual']} de {c['total']}")
            
            cb1, cb2 = st.columns(2)
            if cb1.button(f"PAGAR PARCELA {c['atual']}", key=f"p_{i}"):
                dados['gastos_diarios'].append({"desc": f"Parc. {c['nome']} ({c['atual']}/{c['total']})", "valor": c['valor'], "cat": "Fixo"})
                c['atual'] += 1
                if c['atual'] > c['total']:
                    dados['contas_fixas'].pop(i)
                salvar_dados(dados)
                st.rerun()
            if cb2.button("Excluir Conta", key=f"del_{i}"):
                dados['contas_fixas'].pop(i)
                salvar_dados(dados)
                st.rerun()

with tab3:
    st.subheader("📈 Resumo de Gastos")
    if dados['gastos_diarios']:
        df = pd.DataFrame(dados['gastos_diarios'])
        st.dataframe(df, use_container_width=True)
        
        # Botão para virar quinzena
        st.divider()
        if st.button("🔄 FINALIZAR QUINZENA (Limpar Gastos e Virar)"):
            dados["extra"] = saldo_livre
            dados["salario"] = 0.0
            dados["gastos_diarios"] = []
            dados["quinzena"] = "2ª Quinzena" if dados["quinzena"] == "1ª Quinzena" else "1ª Quinzena"
            salvar_dados(dados)
            st.success("Quinzena virada com sucesso!")
            st.rerun()
    else:
        st.info("Nenhum gasto registrado nesta quinzena.")

# Menu Lateral para Reset
with st.sidebar:
    st.title("⚙️ Configurações")
    if st.button("Sair"):
        st.session_state.autenticado = False
        st.rerun()
    st.divider()
    if st.checkbox("Liberar Reset Total"):
        if st.button("LIMPAR TUDO"):
            if os.path.exists("dados.json"):
                os.remove("dados.json")
                st.rerun()
