import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="Financeiro Pro", layout="centered", page_icon="💰")

# --- ESTILO ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .st-emotion-cache-1r6slb0 { border-radius: 15px; border: 1px solid #30363d; padding: 20px; background-color: #161b22; }
    h1, h2, h3 { color: #58a6ff !important; }
    .stMetric { background-color: #1c2128; padding: 10px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS (PROTEÇÃO CONTRA ERROS) ---
def carregar_dados():
    modelo = {
        "cdb_total": 0.0, "tesouro_total": 0.0, "gastos_diarios": [], 
        "contas_fixas": [], "metas": [], "salario": 0.0, "extra": 0.0, 
        "pct_invest": 10.0
    }
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
    st.markdown("<h1 style='text-align: center;'>🔐 Acesso</h1>", unsafe_allow_html=True)
    with st.container(border=True):
        u = st.text_input("Usuário")
        s = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if u == "giovanne" and s == "8708":
                st.session_state.autenticado = True
                st.rerun()
    st.stop()

# --- CÁLCULOS ---
total_gastos = sum(g.get('valor', 0) for g in dados['gastos_diarios'])
receita_total = dados['salario'] + dados['extra']
saldo_livre = receita_total - total_gastos

# --- DASHBOARD PRINCIPAL ---
st.markdown("<h1 style='text-align: center;'>📱 Financeiro Pro</h1>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("Saldo Livre", formatar_br(saldo_livre))
c2.metric("Total CDB", formatar_br(dados['cdb_total']))
c3.metric("Total Tesouro", formatar_br(dados['tesouro_total']))

tab1, tab2, tab3, tab4 = st.tabs(["💰 Fluxo", "🎯 Investimentos & Metas", "📝 Contas", "📊 Extrato"])

with tab1:
    with st.container(border=True):
        st.subheader("📥 Receitas")
        col_s1, col_s2 = st.columns(2)
        v_sal = col_s1.number_input("Salário", value=float(dados['salario']), format="%.2f")
        v_ext = col_s2.number_input("Extras", value=float(dados['extra']), format="%.2f")
        if v_sal != dados['salario'] or v_ext != dados['extra']:
            dados.update({"salario": v_sal, "extra": v_ext})
            salvar_dados(dados)
            st.rerun()

    with st.container(border=True):
        st.subheader("🛒 Registrar Gasto")
        g_n = st.text_input("O que comprou?")
        g_v = st.number_input("Valor R$", min_value=0.0, format="%.2f")
        g_c = st.selectbox("Categoria", ["Alimentação", "Transporte", "Lazer", "Saúde", "Casa", "Outros"])
        
        with st.popover("✅ Confirmar Registro", use_container_width=True):
            st.write(f"Deseja salvar: **{g_n}** - **{formatar_br(g_v)}**?")
            if st.button("Sim, Registrar"):
                if g_n and g_v > 0:
                    dados['gastos_diarios'].append({
                        "data": datetime.now().strftime("%d/%m %H:%M"),
                        "desc": g_n, "valor": g_v, "cat": g_c
                    })
                    salvar_dados(dados)
                    st.toast("Gasto salvo!", icon="✅")
                    st.rerun()

with tab2:
    with st.container(border=True):
        st.subheader("🏦 Aplicar Investimento")
        v_pct = st.slider("Porcentagem da Receita", 0, 100, int(dados['pct_invest']))
        valor_aplicar = (receita_total * (v_pct / 100)) / 2
        st.write(f"Valor calculado: **{formatar_br(valor_aplicar)}**")
        
        col_inv1, col_inv2 = st.columns(2)
        with col_inv1:
            with st.popover("CDB", use_container_width=True):
                if st.button("Confirmar CDB"):
                    dados['cdb_total'] += valor_aplicar
                    dados['gastos_diarios'].append({"data": datetime.now().strftime("%d/%m"), "desc": "Aplicação CDB", "valor": valor_aplicar, "cat": "Investimento"})
                    dados['pct_invest'] = float(v_pct)
                    salvar_dados(dados)
                    st.rerun()
        with col_inv2:
            with st.popover("Tesouro", use_container_width=True):
                if st.button("Confirmar Tesouro"):
                    dados['tesouro_total'] += valor_aplicar
                    dados['gastos_diarios'].append({"data": datetime.now().strftime("%d/%m"), "desc": "Aplicação Tesouro", "valor": valor_aplicar, "cat": "Investimento"})
                    dados['pct_invest'] = float(v_pct)
                    salvar_dados(dados)
                    st.rerun()

    st.divider()
    st.subheader("🎯 Meus Objetivos")
    with st.expander("+ Criar Novo Objetivo"):
        m_n = st.text_input("Nome do Objetivo")
        m_v = st.number_input("Valor Alvo", min_value=0.0)
        m_tipo = st.selectbox("Usar qual saldo?", ["CDB", "Tesouro", "Total (Ambos)"])
        if st.button("Salvar Meta"):
            dados['metas'].append({"nome": m_n, "alvo": m_v, "tipo": m_tipo})
            salvar_dados(dados)
            st.rerun()

    for i, m in enumerate(dados['metas']):
        with st.container(border=True):
            if m['tipo'] == "CDB": atual = dados['cdb_total']
            elif m['tipo'] == "Tesouro": atual = dados['tesouro_total']
            else: atual = dados['cdb_total'] + dados['tesouro_total']
            
            prog = min(atual / m['alvo'], 1.0) if m['alvo'] > 0 else 0
            faltam = max(m['alvo'] - atual, 0)
            
            st.write(f"**{m['nome']}** ({m['tipo']})")
            st.progress(prog)
            col_met1, col_met2 = st.columns(2)
            col_met1.write(f"**{prog*100:.1f}%**")
            col_met2.write(f"Falta: {formatar_br(faltam)}")
            if st.button("Excluir", key=f"del_meta_{i}"):
                dados['metas'].pop(i)
                salvar_dados(dados)
                st.rerun()

with tab3:
    st.subheader("📅 Parcelas")
    with st.expander("+ Nova Conta Parcelada"):
        nc = st.text_input("Item")
        vc = st.number_input("Valor Parcela", min_value=0.0)
        p_to = st.number_input("Total Parc.", 1, 100)
        st.write(f"Total: {formatar_br(vc * p_to)}")
        if st.button("Adicionar"):
            dados['contas_fixas'].append({"nome": nc, "valor": vc, "atual": 1, "total": p_to})
            salvar_dados(dados)
            st.rerun()

    for i, c in enumerate(dados['contas_fixas']):
        with st.container(border=True):
            st.write(f"**{c['nome']}** | {c['atual']}/{c['total']} de {formatar_br(c['valor'])}")
            with st.popover(f"Pagar Parcela {c['atual']}"):
                if st.button("Confirmar Pagamento", key=f"btn_pag_{i}"):
                    dados['gastos_diarios'].append({"data": datetime.now().strftime("%d/%m"), "desc": f"Parc. {c['nome']}", "valor": c['valor'], "cat": "Fixo"})
                    c['atual'] += 1
                    if c['atual'] > c['total']: dados['contas_fixas'].pop(i)
                    salvar_dados(dados)
                    st.rerun()

with tab4:
    st.subheader("📊 Relatórios")
    if dados['gastos_diarios']:
        df = pd.DataFrame(dados['gastos_diarios'])
        
        # Gráfico Sunburst (Inovador)
        fig = px.sunburst(df, path=['cat', 'desc'], values='valor', 
                          title="Explosão de Gastos (Clique para expandir)",
                          color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("### Últimos 10 Lançamentos")
        df_display = df.tail(10)[::-1].copy()
        df_display['valor'] = df_display['valor'].apply(lambda x: formatar_br(x))
        st.table(df_display)
    else:
        st.info("Sem dados para exibir.")

# SIDEBAR
with st.sidebar:
    if st.button("Sair"):
        st.session_state.autenticado = False
        st.rerun()
    st.divider()
    if st.checkbox("Habilitar Reset"):
        if st.button("Zerar Quinzena"):
            dados["gastos_diarios"] = []
            salvar_dados(dados)
            st.rerun()
