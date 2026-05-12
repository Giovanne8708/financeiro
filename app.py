import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="Financeiro Pro", layout="centered", page_icon="📈")

# --- ESTILO ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .st-emotion-cache-1r6slb0 { border-radius: 15px; border: 1px solid #30363d; padding: 20px; background-color: #161b22; }
    h1, h2, h3 { color: #58a6ff !important; }
    .stMetric { background-color: #1c2128; padding: 10px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE DATA (PROTEÇÃO CONTRA KEYERROR) ---
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
                # Verifica cada chave do modelo; se não existir no arquivo, adiciona
                for chave, valor_padrao in modelo.items():
                    if chave not in d:
                        d[chave] = valor_padrao
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
    st.markdown("<h1 style='text-align: center;'>🔐 Acesso</h1>", unsafe_allow_html=True)
    with st.container(border=True):
        u = st.text_input("Usuário")
        s = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if u == "giovanne" and s == "8708":
                st.session_state.autenticado = True
                st.rerun()
    st.stop()

# --- CÁLCULOS TOTAIS ---
# Usando .get para garantir que não trave se a chave sumir
total_gastos = sum(g.get('valor', 0) for g in dados.get('gastos_diarios', []))
receita_total = dados.get('salario', 0) + dados.get('extra', 0)
saldo_livre = receita_total - total_gastos

# --- INTERFACE PRINCIPAL ---
st.markdown("<h1 style='text-align: center;'>📱 Financeiro Pro</h1>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("Saldo Livre", formatar_br(saldo_livre))
c2.metric("Total CDB", formatar_br(dados.get('cdb_total', 0)))
c3.metric("Total Tesouro", formatar_br(dados.get('tesouro_total', 0)))

tab1, tab2, tab3, tab4 = st.tabs(["💰 Fluxo", "🎯 Metas", "📝 Contas", "📊 Extrato"])

with tab1:
    with st.container(border=True):
        st.subheader("📥 Receitas")
        col_s1, col_s2 = st.columns(2)
        v_sal = col_s1.number_input("Salário", value=float(dados['salario']), format="%.2f")
        v_ext = col_s2.number_input("Extras", value=float(dados['extra']), format="%.2f")
        if v_sal != dados['salario'] or v_ext != dados['extra']:
            dados['salario'] = v_sal
            dados['extra'] = v_ext
            salvar_dados(dados)
            st.rerun()

    with st.container(border=True):
        st.subheader("🛒 Registrar Gasto")
        g_n = st.text_input("O que comprou?")
        g_v = st.number_input("Valor R$", min_value=0.0, format="%.2f")
        g_c = st.selectbox("Categoria", ["Alimentação", "Transporte", "Lazer", "Saúde", "Casa", "Outros", "Investimento"])
        
        with st.popover("Confirmar Registro"):
            st.write(f"Salvar: {g_n} - {formatar_br(g_v)}?")
            if st.button("✅ Confirmar Gasto"):
                if g_n and g_v > 0:
                    dados['gastos_diarios'].append({
                        "data": datetime.now().strftime("%d/%m %H:%M"),
                        "desc": g_n, "valor": g_v, "cat": g_c
                    })
                    salvar_dados(dados)
                    st.rerun()

with tab2:
    with st.container(border=True):
        st.subheader("🏦 Aplicar Investimento")
        v_pct = st.slider("Porcentagem da Receita", 0, 100, int(dados['pct_invest']))
        valor_aplicar = (receita_total * (v_pct / 100)) / 2
        st.write(f"Valor calculado: **{formatar_br(valor_aplicar)}**")
        
        col_inv1, col_inv2 = st.columns(2)
        with col_inv1:
            with st.popover("Investir CDB"):
                if st.button("Confirmar CDB"):
                    dados['cdb_total'] += valor_aplicar
                    dados['gastos_diarios'].append({"data": datetime.now().strftime("%d/%m"), "desc": "Aplicação CDB", "valor": valor_aplicar, "cat": "Investimento"})
                    dados['pct_invest'] = float(v_pct)
                    salvar_dados(dados)
                    st.rerun()
        with col_inv2:
            with st.popover("Investir Tesouro"):
                if st.button("Confirmar Tesouro"):
                    dados['tesouro_total'] += valor_aplicar
                    dados['gastos_diarios'].append({"data": datetime.now().strftime("%d/%m"), "desc": "Aplicação Tesouro", "valor": valor_aplicar, "cat": "Investimento"})
                    dados['pct_invest'] = float(v_pct)
                    salvar_dados(dados)
                    st.rerun()

    st.divider()
    st.subheader("🎯 Meus Objetivos")
    with st.expander("+ Novo Objetivo"):
        m_n = st.text_input("Nome do Objetivo")
        m_v = st.number_input("Valor Alvo", min_value=0.0)
        m_tipo = st.selectbox("Usar qual saldo?", ["CDB", "Tesouro", "Total (Ambos)"])
        if st.button("Salvar Meta"):
            dados['metas'].append({"nome": m_n, "alvo": m_v, "tipo": m_tipo})
            salvar_dados(dados)
            st.rerun()

    for i, m in enumerate(dados.get('metas', [])):
        with st.container(border=True):
            if m.get('tipo') == "CDB": atual = dados.get('cdb_total', 0)
            elif m.get('tipo') == "Tesouro": atual = dados.get('tesouro_total', 0)
            else: atual = dados.get('cdb_total', 0) + dados.get('tesouro_total', 0)
            
            prog = min(atual / m['alvo'], 1.0) if m['alvo'] > 0 else 0
            st.write(f"**{m['nome']}** ({m.get('tipo', 'Total')})")
            st.progress(prog)
            st.write(f"**{prog*100:.1f}%** | Falta: {formatar_br(max(m['alvo']-atual, 0))}")
            if st.button("Excluir", key=f"del_{i}"):
                dados['metas'].pop(i)
                salvar_dados(dados)
                st.rerun()

with tab3:
    st.subheader("📅 Gestão de Contas")
    with st.expander("+ Nova Conta"):
        nc = st.text_input("Item")
        vc = st.number_input("Valor Parcela", min_value=0.0)
        p_to = st.number_input("Total Parc.", 1, 100)
        if st.button("Adicionar Conta"):
            dados['contas_fixas'].append({"nome": nc, "valor": vc, "atual": 1, "total": p_to})
            salvar_dados(dados)
            st.rerun()

    for i, c in enumerate(dados.get('contas_fixas', [])):
        with st.container(border=True):
            st.write(f"**{c['nome']}** | {c['atual']}/{c['total']} de {formatar_br(c['valor'])}")
            with st.popover(f"Pagar Parc. {c['atual']}"):
                if st.button("Confirmar Pagamento", key=f"p_{i}"):
                    dados['gastos_diarios'].append({"data": datetime.now().strftime("%d/%m"), "desc": f"Parc. {c['nome']}", "valor": c['valor'], "cat": "Fixo"})
                    c['atual'] += 1
                    if c['atual'] > c['total']: dados['contas_fixas'].pop(i)
                    salvar_dados(dados)
                    st.rerun()

with tab4:
    st.subheader("📊 Relatórios")
    if dados.get('gastos_diarios'):
        df = pd.DataFrame(dados['gastos_diarios'])
        fig = px.pie(df, values='valor', names='cat', hole=0.4, title="Gastos por Categoria")
        st.plotly_chart(fig, use_container_width=True)
        st.write("### Últimos 10 Lançamentos")
        st.table(df.tail(10)[::-1])
    else:
        st.info("Sem dados.")

with st.sidebar:
    if st.button("Sair"):
        st.session_state.autenticado = False
        st.rerun()
    st.divider()
    if st.checkbox("Ativar Reset Total"):
        if st.button("APAGAR TUDO E REINICIAR"):
            if os.path.exists("dados.json"):
                os.remove("dados.json")
            st.rerun()
