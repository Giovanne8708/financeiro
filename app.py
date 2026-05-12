import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÕES DO APP ---
st.set_page_config(page_title="Financeiro Pro", layout="centered", page_icon="💰")

# --- CSS AVANÇADO ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .section-card {
        background-color: #161b22;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #30363d;
        margin-bottom: 25px;
    }
    h1, h2, h3 { color: #58a6ff !important; }
    .stMetric { background-color: #1f2937 !important; border-radius: 12px; padding: 15px !important; }
    .stButton>button { border-radius: 10px; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE SUPORTE ---
def format_num(valor):
    """Converte texto da interface (ex: 1.081,35) em número real (1081.35)"""
    if isinstance(valor, str):
        # Remove símbolos e garante que o ponto seja o separador decimal
        valor = valor.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
    try:
        return float(valor)
    except:
        return 0.0

def formatar_moeda_br(valor):
    """Converte número real (1081.35) em texto brasileiro (R$ 1.081,35)"""
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def carregar_dados():
    modelo = {"patrimonio": 0.0, "gastos_diarios": [], "contas_fixas": [], "metas": [], "salario": 0.0, "extra": 0.0, "pct": 10.0, "quinzena": "1ª Quinzena"}
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

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>🔐 Financeiro</h1>", unsafe_allow_html=True)
    u = st.text_input("Usuário")
    s = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if u == "giovanne" and s == "8708":
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Incorreto")
    st.stop()

# --- CARREGAMENTO ---
dados = carregar_dados()

# Sidebar
with st.sidebar:
    st.title("⚙️ Sistema")
    if st.button("Sair"):
        st.session_state.autenticado = False
        st.rerun()
    st.divider()
    st.subheader("🚨 Reset")
    confirma = st.checkbox("Desejo apagar tudo")
    if st.button("LIMPAR BANCO DE DADOS"):
        if confirma:
            dados = {"patrimonio": 0.0, "gastos_diarios": [], "contas_fixas": [], "metas": [], "salario": 0.0, "extra": 0.0, "pct": 10.0, "quinzena": "1ª Quinzena"}
            salvar_dados(dados)
            st.rerun()

st.markdown(f"<h1 style='text-align: center;'>📊 Financeiro Pro</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #8b949e;'>{dados['quinzena']}</p>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["💰 Fluxo", "🎯 Metas", "📈 Análise"])

with tab1:
    # --- CARD ENTRADAS ---
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    # Mostramos o valor formatado para o usuário, mas salvamos como float
    txt_sal = col1.text_input("Recebido", value=str(dados['salario']))
    txt_ext = col2.text_input("Extra", value=str(dados['extra']))
    txt_pct = col3.text_input("Meta %", value=str(dados['pct']))
    
    val_sal, val_ext, val_pct = format_num(txt_sal), format_num(txt_ext), format_num(txt_pct)
    
    if (val_sal, val_ext, val_pct) != (dados['salario'], dados['extra'], dados['pct']):
        dados.update({"salario": val_sal, "extra": val_ext, "pct": val_pct})
        salvar_dados(dados)
    st.markdown("</div>", unsafe_allow_html=True)

    # --- CÁLCULOS ---
    total_gastos = sum(g['valor'] for g in dados['gastos_diarios'])
    saldo_livre = (val_sal + val_ext) - total_gastos
    aporte = ((val_sal + val_ext) * (val_pct / 100)) / 2
    
    # Exibição das Métricas
    c_met1, c_met2 = st.columns(2)
    c_met1.metric("DISPONÍVEL AGORA", formatar_moeda_br(saldo_livre), delta=f"Total: {formatar_moeda_br(val_sal+val_ext)}")
    c_met2.metric("INVESTIMENTO (Q)", formatar_moeda_br(aporte))

    # --- INVESTIMENTOS ---
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("🏦 Guardar")
    ci1, ci2 = st.columns(2)
    if ci1.button(f"CDB: {formatar_moeda_br(aporte)}"):
        dados['patrimonio'] += aporte
        dados['gastos_diarios'].append({"desc": "Investimento CDB", "valor": aporte, "cat": "Investimento"})
        salvar_dados(dados)
        st.rerun()
    if ci2.button(f"TESOURO: {formatar_moeda_br(aporte)}"):
        dados['patrimonio'] += aporte
        dados['gastos_diarios'].append({"desc": "Investimento Tesouro", "valor": aporte, "cat": "Investimento"})
        salvar_dados(dados)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # --- CONTAS ---
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("📝 Contas")
    with st.expander("+ Nova Conta"):
        nc = st.text_input("Nome")
        vc = st.text_input("Valor")
        if st.button("Salvar Conta"):
            v_f = format_num(vc)
            if nc and v_f > 0:
                dados['contas_fixas'].append({"nome": nc, "valor": v_f, "atual": 1, "total": 1})
                salvar_dados(dados)
                st.rerun()

    for i, c in enumerate(dados['contas_fixas']):
        col_c1, col_c2, col_c3 = st.columns([2, 1, 1])
        col_c1.write(f"**{c['nome']}**")
        col_c2.write(formatar_moeda_br(c['valor']))
        if col_c3.button("PAGAR", key=f"p_{i}"):
            dados['gastos_diarios'].append({"desc": f"Pago: {c['nome']}", "valor": c['valor'], "cat": "Fixo"})
            dados['contas_fixas'].pop(i)
            salvar_dados(dados)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # --- GASTOS ---
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("🛒 Gasto Rápido")
    gn = st.text_input("O que?", key="gn")
    gv = st.text_input("Valor R$", key="gv")
    gc = st.selectbox("Cat.", ["Alimentação", "Transporte", "Lazer", "Saúde", "Casa", "Outros"])
    if st.button("Lançar"):
        v_g = format_num(gv)
        if gn and v_g > 0:
            dados['gastos_diarios'].append({"desc": gn, "valor": v_g, "cat": gc})
            salvar_dados(dados)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.subheader("🎯 Metas")
    st.metric("Patrimônio Total", formatar_moeda_br(dados['patrimonio']))
    for i, m in enumerate(dados['metas']):
        prog = min(dados['patrimonio'] / m['alvo'], 1.0) if m['alvo'] > 0 else 0
        st.write(f"**{m['nome']}** - {formatar_moeda_br(m['alvo'])}")
        st.progress(prog)
        if st.button(f"Remover {m['nome']}", key=f"rm_{i}"):
            dados['metas'].pop(i)
            salvar_dados(dados)
            st.rerun()

with tab3:
    st.subheader("📈 Análise")
    if dados['gastos_diarios']:
        df = pd.DataFrame(dados['gastos_diarios'])
        fig = px.pie(df, values='valor', names='cat', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True)
    
    st.divider()
    if st.button("🔄 VIRAR QUINZENA"):
        dados["extra"] = saldo_livre
        dados["salario"] = 0.0
        dados["gastos_diarios"] = []
        dados["quinzena"] = "2ª Quinzena" if dados["quinzena"] == "1ª Quinzena" else "1ª Quinzena"
        salvar_dados(dados)
        st.rerun()
