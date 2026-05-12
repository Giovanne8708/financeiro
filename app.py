import streamlit as st
import json
import os
import pandas as pd

# --- CONFIGURAÇÕES DO APP ---
st.set_page_config(page_title="Financeiro Pro", layout="centered", page_icon="💰")

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .st-emotion-cache-1r6slb0 { border-radius: 15px; border: 1px solid #30363d; padding: 20px; background-color: #161b22; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; color: #58a6ff !important; font-weight: 700; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem !important; color: #ffffff !important; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3em; font-weight: bold; border: none; transition: 0.3s; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS ---
def carregar_dados():
    modelo = {
        "cdb_total": 0.0,
        "tesouro_total": 0.0,
        "gastos_diarios": [], 
        "contas_fixas": [], 
        "metas": [],
        "salario": 0.0, 
        "extra": 0.0, 
        "pct": 10.0, 
        "quinzena": "1ª Quinzena"
    }
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

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>🔐 Financeiro</h1>", unsafe_allow_html=True)
    with st.container(border=True):
        u = st.text_input("Usuário")
        s = st.text_input("Senha", type="password")
        if st.button("Acessar"):
            if u == "giovanne" and s == "8708":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Credenciais inválidas")
    st.stop()

# --- CONTEÚDO PRINCIPAL ---
st.markdown("<h1 style='text-align: center;'>📱 Financeiro Pro</h1>", unsafe_allow_html=True)

# Cálculos Base
total_gastos = sum(g['valor'] for g in dados['gastos_diarios'])
saldo_livre = (dados['salario'] + dados['extra']) - total_gastos
investimento_sugerido = ((dados['salario'] + dados['extra']) * (dados['pct'] / 100)) / 2
patrimonio_total = dados['cdb_total'] + dados['tesouro_total']

col_m1, col_m2 = st.columns(2)
col_m1.metric("Saldo Disponível", formatar_br(saldo_livre))
col_m2.metric("Meta de Investimento", formatar_br(investimento_sugerido))

st.divider()

# ABA ADICIONADA: Extrato Mensal
tab1, tab2, tab3, tab4 = st.tabs(["💰 Fluxo Atual", "🎯 Ativos & Metas", "📝 Contas", "📋 Extrato Mensal"])

with tab1:
    with st.container(border=True):
        st.subheader("📥 Entradas")
        c1, c2, c3 = st.columns(3)
        v_sal = c1.number_input("Salário", value=float(dados['salario']), format="%.2f")
        v_ext = c2.number_input("Extras", value=float(dados['extra']), format="%.2f")
        v_pct = c3.number_input("Meta %", value=float(dados['pct']), format="%.1f")
        
        if (v_sal != dados['salario'] or v_ext != dados['extra'] or v_pct != dados['pct']):
            dados.update({"salario": v_sal, "extra": v_ext, "pct": v_pct})
            salvar_dados(dados)
            st.rerun()

    with st.container(border=True):
        st.subheader("🏦 Investir")
        ci1, ci2 = st.columns(2)
        if ci1.button(f"CDB: {formatar_br(investimento_sugerido)}"):
            dados['cdb_total'] += investimento_sugerido
            dados['gastos_diarios'].append({"desc": "Aplicação CDB", "valor": investimento_sugerido, "cat": "Investimento"})
            salvar_dados(dados)
            st.rerun()
        if ci2.button(f"TESOURO: {formatar_br(investimento_sugerido)}"):
            dados['tesouro_total'] += investimento_sugerido
            dados['gastos_diarios'].append({"desc": "Aplicação Tesouro", "valor": investimento_sugerido, "cat": "Investimento"})
            salvar_dados(dados)
            st.rerun()

    with st.container(border=True):
        st.subheader("🛒 Novo Gasto")
        g_n = st.text_input("O que comprou?")
        g_v = st.number_input("Valor R$", min_value=0.0, format="%.2f")
        g_c = st.selectbox("Categoria", ["Alimentação", "Transporte", "Lazer", "Saúde", "Casa", "Outros"])
        if st.button("Registrar Gasto"):
            if g_n and g_v > 0:
                dados['gastos_diarios'].append({"desc": g_n, "valor": g_v, "cat": g_c})
                salvar_dados(dados)
                st.rerun()

with tab2:
    st.markdown("<h2 style='text-align: center;'>📈 Meus Ativos</h2>", unsafe_allow_html=True)
    c_cdb, c_tes = st.columns(2)
    with c_cdb:
        with st.container(border=True):
            st.markdown("### 💎 CDB")
            st.markdown(f"**{formatar_br(dados['cdb_total'])}**")
    with c_tes:
        with st.container(border=True):
            st.markdown("### 🏛️ Tesouro")
            st.markdown(f"**{formatar_br(dados['tesouro_total'])}**")
    
    st.divider()
    st.subheader("🎯 Metas")
    with st.expander("+ Novo Objetivo"):
        m_nome = st.text_input("Objetivo")
        m_valor = st.number_input("Quanto custa? R$", min_value=0.0, format="%.2f")
        if st.button("Criar Meta"):
            if m_nome and m_valor > 0:
                dados['metas'].append({"nome": m_nome, "alvo": m_valor})
                salvar_dados(dados)
                st.rerun()

    for i, m in enumerate(dados['metas']):
        with st.container(border=True):
            st.markdown(f"**{m['nome']}** - {formatar_br(m['alvo'])}")
            prog = min(patrimonio_total / m['alvo'], 1.0) if m['alvo'] > 0 else 0
            st.progress(prog)
            if st.button("Remover Meta", key=f"del_m_{i}"):
                dados['metas'].pop(i)
                salvar_dados(dados)
                st.rerun()

with tab3:
    st.subheader("📅 Parcelas")
    with st.expander("+ Adicionar Conta"):
        nc = st.text_input("Item")
        vc = st.number_input("Valor Parcela", min_value=0.0, format="%.2f")
        p_at = st.number_input("Parc. Atual", 1, 100, 1)
        p_to = st.number_input("Total Parc.", 1, 100, 1)
        if st.button("Salvar"):
            if nc and vc > 0:
                dados['contas_fixas'].append({"nome": nc, "valor": vc, "atual": p_at, "total": p_to})
                salvar_dados(dados)
                st.rerun()

    for i, c in enumerate(dados['contas_fixas']):
        with st.container(border=True):
            st.markdown(f"**{c['nome']}** - {formatar_br(c['valor'])}")
            st.progress(c['atual'] / c['total'])
            if st.button(f"PAGAR PARCELA {c['atual']}", key=f"pag_{i}"):
                dados['gastos_diarios'].append({"desc": f"Parc. {c['nome']}", "valor": c['valor'], "cat": "Fixo"})
                c['atual'] += 1
                if c['atual'] > c['total']: dados['contas_fixas'].pop(i)
                salvar_dados(dados)
                st.rerun()

# NOVA ABA IMPLEMENTADA
with tab4:
    st.subheader("📋 Extrato de Gastos")
    if dados['gastos_diarios']:
        # Criar Tabela organizada
        df = pd.DataFrame(dados['gastos_diarios'])
        df.columns = ["Descrição", "Valor (R$)", "Categoria"]
        
        # Mostrar o total gasto no topo do extrato
        st.markdown(f"### Total Gasto nesta Quinzena: <span style='color:#ff4b4b'>{formatar_br(total_gastos)}</span>", unsafe_allow_html=True)
        
        # Exibir a tabela
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.divider()
        st.caption("Dica: Use o botão de Virar Quinzena no menu lateral para limpar este extrato ao mudar de mês.")
    else:
        st.info("Nenhum gasto registrado até agora.")

# Sidebar
with st.sidebar:
    st.title("⚙️ Sistema")
    st.write(f"Período: **{dados['quinzena']}**")
    if st.button("Sair"):
        st.session_state.autenticado = False
        st.rerun()
    st.divider()
    if st.button("🔄 VIRAR QUINZENA"):
        dados["extra"] = saldo_livre
        dados["salario"] = 0.0
        dados["gastos_diarios"] = []
        dados["quinzena"] = "2ª Quinzena" if dados["quinzena"] == "1ª Quinzena" else "1ª Quinzena"
        salvar_dados(dados)
        st.success("Dados resetados para a nova quinzena!")
        st.rerun()
    st.divider()
    if st.checkbox("Liberar Reset"):
        if st.button("APAGAR TUDO"):
            if os.path.exists("dados.json"): os.remove("dados.json")
            st.rerun()
