import streamlit as st
import json
import os

# --- CONFIGURAÇÕES DE SEGURANÇA ---
USUARIO_CORRETO = "giovanne"
SENHA_CORRETA = "8708" 

# Configuração da Página para Mobile
st.set_page_config(page_title="Status Fluxo", layout="centered")

# Estilo CSS para imitar seu programa original
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #1f2937; color: white; }
    .stMetric { background-color: #111827; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    label { color: #58a6ff !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def verificar_login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False
    if not st.session_state["autenticado"]:
        st.title("🔐 Acesso")
        u = st.text_input("Usuário")
        s = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if u == USUARIO_CORRETO and s == SENHA_CORRETA:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Incorreto")
        return False
    return True

def carregar_dados():
    if os.path.exists("dados.json"):
        with open("dados.json", "r") as f:
            return json.load(f)
    return {"patrimonio": 0.0, "gastos_diarios": [], "contas_fixas": [], "metas": []}

def salvar_dados(dados):
    with open("dados.json", "w") as f:
        json.dump(dados, f, indent=4)

if verificar_login():
    dados = carregar_dados()

    # Título Principal
    st.title("📊 Status Fluxo Mobile")

    tab1, tab2, tab3 = st.tabs(["💰 Fluxo de Caixa", "🎯 Metas", "⚙️ Config"])

    with tab1:
        # --- SEÇÃO DE ENTRADAS ---
        st.subheader("Configuração Geral")
        col_sal, col_ext = st.columns(2)
        salario = col_sal.number_input("Seu Salário (R$)", value=0.0)
        extra = col_ext.number_input("Renda Extra (R$)", value=0.0)
        
        # Cálculo de Saldo
        total_contas = sum(c['valor'] for c in dados['contas_fixas'])
        total_gastos = sum(g['valor'] for g in dados['gastos_diarios'])
        saldo_livre = (salario + extra) - total_contas - total_gastos
        
        st.metric("DISPONÍVEL PARA GASTAR", f"R$ {saldo_livre:.2f}")

        st.divider()

        # --- SEÇÃO DE CONTAS E PARCELAS (IGUAL AO SEU PRINT) ---
        st.subheader("📝 Contas e Parcelas")
        with st.expander("Adicionar Nova Conta"):
            c_nome = st.text_input("Nome da Conta")
            c_val = st.number_input("Valor da Parcela (R$)", min_value=0.0)
            c_atu = st.number_input("Parcela Atual", min_value=1, step=1)
            c_tot = st.number_input("Parcela Total", min_value=1, step=1)
            
            if st.button("ADICIONAR CONTA"):
                if c_nome and c_val > 0:
                    dados['contas_fixas'].append({
                        "nome": c_nome, "valor": c_val, "atual": c_atu, "total": c_tot
                    })
                    salvar_dados(dados)
                    st.success("Conta adicionada!")
                    st.rerun()

        # Mostrar lista de contas
        for i, c in enumerate(dados['contas_fixas']):
            col_t, col_b = st.columns([3, 1])
            col_t.write(f"**{c['nome']}** ({c['atual']}/{c['total']}) - R$ {c['valor']:.2f}")
            if col_b.button("🗑️", key=f"del_c_{i}"):
                dados['contas_fixas'].pop(i)
                salvar_dados(dados)
                st.rerun()

        st.divider()

        # --- SEÇÃO DE GASTOS DIÁRIOS (IGUAL AO SEU PRINT) ---
        st.subheader("🛍️ Gastos da Quinzena")
        g_desc = st.text_input("Descrição (O que comprou?)")
        g_val = st.number_input("Valor R$", min_value=0.0, key="gasto_valor")
        
        if st.button("LANÇAR GASTO", type="primary"):
            if g_desc and g_val > 0:
                dados['gastos_diarios'].append({"desc": g_desc, "valor": g_val})
                salvar_dados(dados)
                st.rerun()

        # Lista de Gastos
        for i, g in enumerate(reversed(dados['gastos_diarios'])):
            col_gt, col_gb = st.columns([3, 1])
            col_gt.write(f"• {g['desc']}: R$ {g['valor']:.2f}")
            # Botão para apagar gasto se errar
            if col_gb.button("x", key=f"del_g_{i}"):
                dados['gastos_diarios'].remove(g)
                salvar_dados(dados)
                st.rerun()

    with tab2:
        st.subheader("🎯 Metas de Patrimônio")
        st.write(f"**Total Acumulado: R$ {dados['patrimonio']:.2f}**")
        
        with st.expander("Nova Meta"):
            m_nome = st.text_input("Objetivo")
            m_alvo = st.number_input("Valor Alvo (R$)", min_value=0.0)
            if st.button("Criar Meta"):
                dados['metas'].append({"nome": m_nome, "alvo": m_alvo})
                salvar_dados(dados)
                st.rerun()

        for m in dados['metas']:
            prog = min(dados['patrimonio'] / m['alvo'], 1.0) if m['alvo'] > 0 else 0
            st.write(f"**{m['nome']}** (Alvo: R$ {m['alvo']:.2f})")
            st.progress(prog)

    with tab3:
        st.subheader("Configurações de Dados")
        if st.button("LIMPAR TUDO (RESET)"):
            if st.checkbox("Confirmar exclusão de todos os dados?"):
                dados = {"patrimonio": 0.0, "gastos_diarios": [], "contas_fixas": [], "metas": []}
                salvar_dados(dados)
                st.rerun()
        
        if st.sidebar.button("Sair"):
            st.session_state["autenticado"] = False
            st.rerun()
