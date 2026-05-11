import streamlit as st
import json
import os

# --- CONFIGURAÇÕES DE ACESSO ---
USUARIO_CORRETO = "giovanne"
SENHA_CORRETA = "8708" 

st.set_page_config(page_title="Status Fluxo", layout="centered")

# Estilo para botões e métricas
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .stMetric { background-color: #0e1117; padding: 10px; border-radius: 10px; border: 1px solid #30363d; }
    div[data-testid="stExpander"] { border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

def verificar_login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False
    if not st.session_state["autenticado"]:
        st.title("🔐 Acesso Restrito")
        u = st.text_input("Usuário")
        s = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if u == USUARIO_CORRETO and s == SENHA_CORRETA:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")
        return False
    return True

def carregar_dados():
    if os.path.exists("dados.json"):
        with open("dados.json", "r") as f:
            return json.load(f)
    return {"patrimonio": 0.0, "gastos_diarios": [], "contas_fixas": [], "metas": [], "salario": 0.0, "extra": 0.0, "pct": 10.0}

def salvar_dados(dados):
    with open("dados.json", "w") as f:
        json.dump(dados, f, indent=4)

if verificar_login():
    dados = carregar_dados()

    st.title("📊 Status Fluxo Mobile")

    tab1, tab2, tab3 = st.tabs(["💰 Fluxo de Caixa", "🎯 Metas e Patrimônio", "⚙️ Ajustes"])

    with tab1:
        # --- 1. CONFIGURAÇÃO E SALDO ---
        col_s, col_e, col_p = st.columns(3)
        salario = col_s.number_input("Salário", value=float(dados.get("salario", 0)))
        extra = col_e.number_input("Extra", value=float(dados.get("extra", 0)))
        pct = col_p.number_input("Meta %", value=float(dados.get("pct", 10)))
        
        # Salva as configs se mudarem
        if salario != dados["salario"] or extra != dados["extra"] or pct != dados["pct"]:
            dados.update({"salario": salario, "extra": extra, "pct": pct})
            salvar_dados(dados)

        # Cálculo do Aporte Sugerido (Igual ao seu Python)
        aporte_sugerido = ((salario + extra) * (pct / 100)) / 2
        
        # Cálculo do Saldo Livre
        total_saidas = sum(g['valor'] for g in dados['gastos_diarios']) + sum(c['valor'] for c in dados['contas_fixas'])
        saldo_livre = (salario + extra) - total_saidas
        
        st.metric("SALDO LIVRE ATUAL", f"R$ {saldo_livre:.2f}")

        st.divider()

        # --- 2. INVESTIMENTOS (GUARDAR DINHEIRO) ---
        st.subheader("🏦 Guardar nos Investimentos")
        c1, c2 = st.columns(2)
        
        with c1:
            st.write(f"**CDB**")
            st.write(f"R$ {aporte_sugerido:.2f}")
            if st.button("GUARDAR CDB"):
                dados['patrimonio'] += aporte_sugerido
                dados['gastos_diarios'].append({"desc": "Guardou: CDB", "valor": aporte_sugerido})
                salvar_dados(dados)
                st.rerun()

        with c2:
            st.write(f"**Tesouro**")
            st.write(f"R$ {aporte_sugerido:.2f}")
            if st.button("GUARDAR TESOURO"):
                dados['patrimonio'] += aporte_sugerido
                dados['gastos_diarios'].append({"desc": "Guardou: Tesouro", "valor": aporte_sugerido})
                salvar_dados(dados)
                st.rerun()

        st.divider()

        # --- 3. CONTAS E GASTOS ---
        col_contas, col_gastos = st.columns(2)

        with col_contas:
            st.subheader("📝 Contas Fixas")
            with st.expander("+ Nova Conta"):
                n_c = st.text_input("Item")
                v_c = st.number_input("Valor R$", min_value=0.0, key="v_c")
                if st.button("Adicionar"):
                    dados['contas_fixas'].append({"nome": n_c, "valor": v_c})
                    salvar_dados(dados)
                    st.rerun()
            
            for i, c in enumerate(dados['contas_fixas']):
                st.caption(f"{c['nome']}: R$ {c['valor']:.2f}")
                if st.button("Remover", key=f"rc_{i}"):
                    dados['contas_fixas'].pop(i)
                    salvar_dados(dados)
                    st.rerun()

        with col_gastos:
            st.subheader("🛍️ Gastos Diários")
            with st.expander("+ Lançar Gasto"):
                g_d = st.text_input("Descrição")
                g_v = st.number_input("Valor R$", min_value=0.0, key="g_v")
                if st.button("Lançar"):
                    dados['gastos_diarios'].append({"desc": g_d, "valor": g_v})
                    salvar_dados(dados)
                    st.rerun()
            
            for i, g in enumerate(reversed(dados['gastos_diarios'][-5:])): # Mostra os últimos 5
                st.caption(f"{g['desc']}: R$ {g['valor']:.2f}")

    with tab2:
        st.subheader("💰 Patrimônio Total")
        st.title(f"R$ {dados['patrimonio']:.2f}")
        
        st.divider()
        st.subheader("🎯 Suas Metas")
        with st.expander("+ Criar Objetivo"):
            m_n = st.text_input("Nome da Meta")
            m_v = st.number_input("Valor Alvo", min_value=0.0, key="m_v")
            if st.button("Salvar Meta"):
                dados['metas'].append({"nome": m_n, "alvo": m_v})
                salvar_dados(dados)
                st.rerun()

        for i, m in enumerate(dados['metas']):
            prog = min(dados['patrimonio'] / m['alvo'], 1.0) if m['alvo'] > 0 else 0
            st.write(f"**{m['nome']}**")
            st.progress(prog)
            st.write(f"R$ {dados['patrimonio']:.2f} de R$ {m['alvo']:.2f}")
            if st.button("Excluir Meta", key=f"rm_{i}"):
                dados['metas'].pop(i)
                salvar_dados(dados)
                st.rerun()

    with tab3:
        if st.button("Sair / Logout"):
            st.session_state["autenticado"] = False
            st.rerun()
        
        if st.button("LIMPAR TODOS OS DADOS", type="primary"):
            dados = {"patrimonio": 0.0, "gastos_diarios": [], "contas_fixas": [], "metas": [], "salario": 0.0, "extra": 0.0, "pct": 10.0}
            salvar_dados(dados)
            st.rerun()
