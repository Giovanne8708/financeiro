import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="Financeiro Pro 2.0", layout="wide", page_icon="🚀")

# --- ESTILO CSS AVANÇADO ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    div[data-testid="stMetricValue"] { color: #58a6ff; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #161b22;
        border-radius: 10px 10px 0px 0px;
        padding: 10px 20px;
        color: white;
    }
    .status-card {
        background-color: #1c2128;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #58a6ff;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS ---
def carregar_dados():
    modelo = {"cdb_total": 0.0, "tesouro_total": 0.0, "gastos_diarios": [], "contas_fixas": [], "metas": [], "salario": 0.0, "extra": 0.0, "pct_invest": 10.0}
    if os.path.exists("dados.json"):
        try:
            with open("dados.json", "r") as f:
                d = json.load(f)
                for k, v in modelo.items():
                    if k not in d: d[k] = v
                return d
        except: return modelo
    return modelo

def salvar_dados(dados):
    with open("dados.json", "w") as f:
        json.dump(dados, f, indent=4)

def formatar_br(valor):
    return f"R$ {float(valor):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# --- INICIALIZAÇÃO ---
dados = carregar_dados()
if "autenticado" not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>🔐 Login</h1>", unsafe_allow_html=True)
    with st.columns([1,2,1])[1]:
        with st.container(border=True):
            u = st.text_input("Usuário")
            s = st.text_input("Senha", type="password")
            if st.button("Acessar Sistema"):
                if u == "giovanne" and s == "8708":
                    st.session_state.autenticado = True
                    st.rerun()
    st.stop()

# --- LÓGICA DE CÁLCULOS ---
total_gastos = sum(g.get('valor', 0) for g in dados['gastos_diarios'])
receita_total = dados['salario'] + dados['extra']
saldo_livre = receita_total - total_gastos

# --- HEADER INOVADOR ---
st.markdown("<h1 style='text-align: center;'>💎 Dashboard Financeiro</h1>", unsafe_allow_html=True)

# Cards de topo (KPIs)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Disponível", formatar_br(saldo_livre))
c2.metric("Investido CDB", formatar_br(dados['cdb_total']))
c3.metric("Investido Tesouro", formatar_br(dados['tesouro_total']))
c4.metric("Total Gastos", formatar_br(total_gastos), delta=f"-{formatar_br(total_gastos)}", delta_color="inverse")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["💸 Operações", "🎯 Metas & Ativos", "🗓️ Compromissos", "📊 Inteligência Visual"])

with tab1:
    col_a, col_b = st.columns(2)
    
    with col_a:
        with st.container(border=True):
            st.subheader("📥 Rendas")
            v_sal = st.number_input("Salário Líquido", value=float(dados['salario']), format="%.2f")
            v_ext = st.number_input("Renda Extra", value=float(dados['extra']), format="%.2f")
            if st.button("Atualizar Saldo"):
                dados['salario'], dados['extra'] = v_sal, v_ext
                salvar_dados(dados)
                st.toast("Rendas atualizadas!", icon="💰")

    with col_b:
        with st.container(border=True):
            st.subheader("🛒 Novo Lançamento")
            g_n = st.text_input("Descrição", placeholder="Ex: Mercado Central")
            g_v = st.number_input("Valor", min_value=0.0, format="%.2f")
            g_c = st.selectbox("Categoria", ["Alimentação", "Transporte", "Lazer", "Saúde", "Casa", "Investimento", "Outros"])
            
            with st.popover("🚀 Finalizar Lançamento", use_container_width=True):
                st.write("Confirma os detalhes?")
                st.info(f"**{g_n}** | {formatar_br(g_v)}")
                if st.button("Confirmar", key="conf_gasto"):
                    if g_n and g_v > 0:
                        with st.status("Registrando...", expanded=False):
                            dados['gastos_diarios'].append({
                                "data": datetime.now().strftime("%d/%m %H:%M"),
                                "desc": g_n, "valor": g_v, "cat": g_c
                            })
                            salvar_dados(dados)
                        st.toast("Gasto registrado com sucesso!", icon="✅")
                        st.rerun()

with tab2:
    st.subheader("🏦 Gestão de Patrimônio")
    v_pct = st.select_slider("Quanto da sua renda deseja investir?", options=[0, 5, 10, 15, 20, 30, 50], value=int(dados['pct_invest']))
    valor_sugerido = (receita_total * (v_pct / 100)) / 2
    
    col_inv1, col_inv2 = st.columns(2)
    with col_inv1:
        if st.button(f"Mandar {formatar_br(valor_sugerido)} para CDB", use_container_width=True):
            dados['cdb_total'] += valor_sugerido
            dados['gastos_diarios'].append({"data": datetime.now().strftime("%d/%m"), "desc": "Aporte CDB", "valor": valor_sugerido, "cat": "Investimento"})
            dados['pct_invest'] = float(v_pct)
            salvar_dados(dados)
            st.success("CDB Incrementado!")
            st.rerun()
            
    with col_inv2:
        if st.button(f"Mandar {formatar_br(valor_sugerido)} para Tesouro", use_container_width=True):
            dados['tesouro_total'] += valor_sugerido
            dados['gastos_diarios'].append({"data": datetime.now().strftime("%d/%m"), "desc": "Aporte Tesouro", "valor": valor_sugerido, "cat": "Investimento"})
            dados['pct_invest'] = float(v_pct)
            salvar_dados(dados)
            st.success("Tesouro Incrementado!")
            st.rerun()

    st.divider()
    st.subheader("🎯 Progresso de Sonhos")
    for i, m in enumerate(dados['metas']):
        # Lógica de cálculo conforme o tipo escolhido
        if m.get('tipo') == "CDB": atual = dados['cdb_total']
        elif m.get('tipo') == "Tesouro": atual = dados['tesouro_total']
        else: atual = dados['cdb_total'] + dados['tesouro_total']
        
        prog = min(atual / m['alvo'], 1.0) if m['alvo'] > 0 else 0
        
        st.markdown(f"""
        <div class="status-card">
            <b>{m['nome']}</b> | Foco: {m.get('tipo', 'Total')}<br>
            <small>Progresso: {prog*100:.1f}% - Falta {formatar_br(max(m['alvo']-atual, 0))}</small>
        </div>
        """, unsafe_allow_html=True)
        st.progress(prog)

with tab4:
    st.subheader("🔍 Inteligência de Gastos")
    
    if dados['gastos_diarios']:
        df = pd.DataFrame(dados['gastos_diarios'])
        
        # --- GRÁFICO INOVADOR: SUNBURST ---
        # Ele mostra Categoria -> Descrição de forma hierárquica
        fig = px.sunburst(df, path=['cat', 'desc'], values='valor',
                          color='cat', title="Mapa de Calor de Gastos",
                          color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(margin=dict(t=40, l=0, r=0, b=0), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        
        # --- HISTÓRICO ESTILIZADO ---
        st.write("### 📜 Linha do Tempo")
        for _, row in df.tail(10)[::-1].iterrows():
            emoji = "🔴" if row['cat'] != "Investimento" else "🟢"
            with st.container():
                c_data, c_info, c_val = st.columns([1, 3, 1])
                c_data.caption(row['data'])
                c_info.write(f"{emoji} **{row['desc']}** ({row['cat']})")
                c_val.write(f"**{formatar_br(row['valor'])}**")
                st.divider()
    else:
        st.info("Aguardando os primeiros dados para gerar o gráfico.")

# SIDEBAR
with st.sidebar:
    st.title("Configurações")
    if st.button("Limpar Histórico Quinzena"):
        dados['gastos_diarios'] = []
        salvar_dados(dados)
        st.rerun()
    st.divider()
    if st.checkbox("Modo Engenharia"):
        st.json(dados)
