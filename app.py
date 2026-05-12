import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÕES DO APP ---
st.set_page_config(page_title="Financeiro Pro", layout="centered", page_icon="💰")

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .st-emotion-cache-1r6slb0 { border-radius: 15px; border: 1px solid #30363d; padding: 20px; background-color: #161b22; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; color: #58a6ff !important; font-weight: 700; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem !important; color: #ffffff !important; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS ---
def carregar_dados():
    modelo = {
        "cdb_total": 0.0, "tesouro_total": 0.0, "gastos_diarios": [], 
        "contas_fixas": [], "metas": [], "salario": 0.0, "extra": 0.0, 
        "pct_invest": 10.0, "quinzena": "1ª Quinzena"
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
            if u == "admin" and s == "1234":
                st.session_state.autenticado = True
                st.rerun()
    st.stop()

# --- CÁLCULOS GERAIS ---
total_gastos = sum(g['valor'] for g in dados['gastos_diarios'])
receita_total = dados['salario'] + dados['extra']
saldo_livre = receita_total - total_gastos
patrimonio_total = dados['cdb_total'] + dados['tesouro_total']

# --- INTERFACE ---
st.markdown("<h1 style='text-align: center;'>📱 Financeiro Pro</h1>", unsafe_allow_html=True)

col_m1, col_m2 = st.columns(2)
col_m1.metric("Saldo Disponível", formatar_br(saldo_livre))
col_m2.metric("Patrimônio Total", formatar_br(patrimonio_total))

tab1, tab2, tab3, tab4 = st.tabs(["💰 Fluxo", "🎯 Investimentos/Metas", "📝 Contas", "📊 Extrato"])

with tab1:
    # 1. ENTRADA (Meta % removida daqui)
    with st.container(border=True):
        st.subheader("📥 Entradas")
        c1, c2 = st.columns(2)
        v_sal = c1.number_input("Salário", value=float(dados['salario']), format="%.2f")
        v_ext = c2.number_input("Extras", value=float(dados['extra']), format="%.2f")
        if (v_sal != dados['salario'] or v_ext != dados['extra']):
            dados.update({"salario": v_sal, "extra": v_ext})
            salvar_dados(dados)
            st.rerun()

    # 3. GASTOS COM CONFIRMAÇÃO
    with st.container(border=True):
        st.subheader("🛒 Novo Gasto")
        g_n = st.text_input("Descrição")
        g_v = st.number_input("Valor R$", min_value=0.0, format="%.2f", key="g_val")
        g_c = st.selectbox("Categoria", ["Alimentação", "Transporte", "Lazer", "Saúde", "Casa", "Outros"])
        
        if st.button("Registrar Gasto"):
            if g_n and g_v > 0:
                st.session_state.confirm_gasto = {"desc": g_n, "valor": g_v, "cat": g_c}
        
        if "confirm_gasto" in st.session_state:
            st.warning(f"Confirmar gasto de {formatar_br(st.session_state.confirm_gasto['valor'])}?")
            if st.button("SIM, REGISTRAR"):
                dados['gastos_diarios'].append(st.session_state.confirm_gasto)
                salvar_dados(dados)
                del st.session_state.confirm_gasto
                st.rerun()

with tab2:
    # 2. INVESTIR COM % E CONFIRMAÇÃO
    with st.container(border=True):
        st.subheader("🏦 Investimento")
        v_pct = st.slider("Escolha a % para investir", 0, 100, int(dados['pct_invest']))
        valor_investir = (receita_total * (v_pct / 100)) / 2 # Dividido por 2 quinzenas
        
        st.write(f"Valor calculado para investir: **{formatar_br(valor_investir)}**")
        
        ci1, ci2 = st.columns(2)
        if ci1.button("APLICAR CDB"):
            st.session_state.tipo_inv = ("cdb_total", valor_investir, "CDB")
        if ci2.button("APLICAR TESOURO"):
            st.session_state.tipo_inv = ("tesouro_total", valor_investir, "Tesouro")
            
        if "tipo_inv" in st.session_state:
            chave, valor, nome = st.session_state.tipo_inv
            st.info(f"Confirmar aplicação de {formatar_br(valor)} no {nome}?")
            if st.button("CONFIRMAR INVESTIMENTO"):
                dados[chave] += valor
                dados['gastos_diarios'].append({"desc": f"Investimento {nome}", "valor": valor, "cat": "Investimento"})
                dados['pct_invest'] = float(v_pct)
                salvar_dados(dados)
                del st.session_state.tipo_inv
                st.rerun()

    # 4. STATUS DAS METAS COM % E FALTA
    st.divider()
    st.subheader("🎯 Objetivos")
    for i, m in enumerate(dados['metas']):
        with st.container(border=True):
            prog = min(patrimonio_total / m['alvo'], 1.0) if m['alvo'] > 0 else 0
            faltam = max(m['alvo'] - patrimonio_total, 0)
            
            st.write(f"**{m['nome']}**")
            st.progress(prog)
            col_a, col_b = st.columns(2)
            col_a.write(f"Status: **{prog*100:.1f}%**")
            col_b.write(f"Falta: **{formatar_br(faltam)}**")
            if st.button("Excluir Meta", key=f"del_m_{i}"):
                dados['metas'].pop(i)
                salvar_dados(dados)
                st.rerun()

with tab3:
    # 5. CONTAS COM CÁLCULO TOTAL E CONFIRMAÇÃO
    st.subheader("📅 Gestão de Contas")
    with st.expander("+ Adicionar Conta Parcelada"):
        nc = st.text_input("Item")
        vc = st.number_input("Valor da Parcela", min_value=0.0, format="%.2f")
        p_to = st.number_input("Total de Parcelas", 1, 100, 1)
        valor_total_conta = vc * p_to
        st.write(f"Valor Total do Contrato: **{formatar_br(valor_total_conta)}**")
        
        if st.button("Salvar Parcelamento"):
            if nc and vc > 0:
                dados['contas_fixas'].append({"nome": nc, "valor": vc, "atual": 1, "total": p_to})
                salvar_dados(dados)
                st.rerun()

    for i, c in enumerate(dados['contas_fixas']):
        with st.container(border=True):
            st.write(f"**{c['nome']}** | Parcela: {formatar_br(c['valor'])}")
            st.caption(f"Progresso: {c['atual']}/{c['total']} | Total: {formatar_br(c['valor'] * c['total'])}")
            
            if st.button(f"PAGAR PARCELA {c['atual']}", key=f"pag_{i}"):
                st.session_state.confirm_pag = i
            
            if st.session_state.get("confirm_pag") == i:
                st.warning(f"Confirmar pagamento da parcela {c['atual']} de {c['nome']}?")
                if st.button("CONFIRMAR PAGAMENTO"):
                    dados['gastos_diarios'].append({"desc": f"Parc. {c['nome']}", "valor": c['valor'], "cat": "Fixo"})
                    c['atual'] += 1
                    if c['atual'] > c['total']: dados['contas_fixas'].pop(i)
                    salvar_dados(dados)
                    del st.session_state.confirm_pag
                    st.rerun()

with tab4:
    # 6. EXTRATO COM GRÁFICO
    st.subheader("📋 Relatório Mensal")
    if dados['gastos_diarios']:
        df = pd.DataFrame(dados['gastos_diarios'])
        
        # Gráfico por Categoria
        fig = px.pie(df, values='valor', names='cat', title="Distribuição de Gastos", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("### Detalhes")
        st.dataframe(df, use_container_width=True)
        st.metric("Total Gasto", formatar_br(total_gastos))
    else:
        st.info("Sem dados de gastos.")

# Sidebar
with st.sidebar:
    st.title("⚙️ Sistema")
    if st.button("Sair"):
        st.session_state.autenticado = False
        st.rerun()
    st.divider()
    if st.button("🔄 VIRAR QUINZENA"):
        dados["extra"] = saldo_livre
        dados["salario"] = 0.0
        dados["gastos_diarios"] = []
        salvar_dados(dados)
        st.rerun()
