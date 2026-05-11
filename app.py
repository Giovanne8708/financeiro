import streamlit as st
import json
import os

# --- CONFIGURAÇÕES DE ACESSO ---
USUARIO_CORRETO = "giovanne"
SENHA_CORRETA = "8708" 

st.set_page_config(page_title="Status Fluxo", layout="centered")

# Estilo visual
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .stMetric { background-color: #0e1117; padding: 10px; border-radius: 10px; border: 1px solid #30363d; }
    .conta-card { background-color: #161b22; padding: 10px; border-radius: 8px; border-left: 5px solid #58a6ff; margin-bottom: 10px; }
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
                st.error("Dados incorretos")
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

    st.title("📊 Status Fluxo Pro")

    tab1, tab2, tab3 = st.tabs(["💰 Fluxo e Pagamentos", "🎯 Patrimônio", "⚙️ Ajustes"])

    with tab1:
        # --- SALDO E CONFIG ---
        col_s, col_e, col_p = st.columns(3)
        salario = col_s.number_input("Salário", value=float(dados.get("salario", 0)))
        extra = col_e.number_input("Extra", value=float(dados.get("extra", 0)))
        pct = col_p.number_input("Meta %", value=float(dados.get("pct", 10)))
        
        if salario != dados["salario"] or extra != dados["extra"] or pct != dados["pct"]:
            dados.update({"salario": salario, "extra": extra, "pct": pct})
            salvar_dados(dados)

        aporte_sugerido = ((salario + extra) * (pct / 100)) / 2
        total_saidas = sum(g['valor'] for g in dados['gastos_diarios'])
        saldo_livre = (salario + extra) - total_saidas
        
        st.metric("SALDO LIVRE (PÓS GASTOS)", f"R$ {saldo_livre:.2f}")

        # --- INVESTIMENTOS ---
        st.subheader("🏦 Guardar Valor Sugerido")
        c1, c2 = st.columns(2)
        with c1:
            if st.button(f"CDB: R$ {aporte_sugerido:.2f}"):
                dados['patrimonio'] += aporte_sugerido
                dados['gastos_diarios'].append({"desc": "Investido: CDB", "valor": aporte_sugerido})
                salvar_dados(dados)
                st.rerun()
        with c2:
            if st.button(f"TESOURO: R$ {aporte_sugerido:.2f}"):
                dados['patrimonio'] += aporte_sugerido
                dados['gastos_diarios'].append({"desc": "Investido: Tesouro", "valor": aporte_sugerido})
                salvar_dados(dados)
                st.rerun()

        st.divider()

        # --- CONTAS COM PARCELAS ---
        st.subheader("📝 Contas e Parcelas")
        with st.expander("+ Adicionar Carnê/Conta"):
            n_c = st.text_input("Nome da Conta")
            v_c = st.number_input("Valor da Parcela R$", min_value=0.0)
            p_a = st.number_input("Parcela Atual", min_value=1, value=1)
            p_t = st.number_input("Total de Parcelas", min_value=1, value=1)
            if st.button("Salvar Conta"):
                dados['contas_fixas'].append({"nome": n_c, "valor": v_c, "atual": p_a, "total": p_t})
                salvar_dados(dados)
                st.rerun()

        for i, c in enumerate(dados['contas_fixas']):
            st.markdown(f"""<div class='conta-card'>
                <b>{c['nome']}</b><br>
                Parcela: {c['atual']}/{c['total']} | R$ {c['valor']:.2f}
                </div>""", unsafe_allow_html=True)
            
            col_p1, col_p2 = st.columns(2)
            if col_p1.button(f"PAGAR PARCELA {c['atual']}", key=f"pay_{i}"):
                # Registra o gasto no saldo do mês
                dados['gastos_diarios'].append({"desc": f"Pago: {c['nome']} ({c['atual']}/{c['total']})", "valor": c['valor']})
                # Sobe a parcela
                c['atual'] += 1
                # Se acabou as parcelas, remove a conta
                if c['atual'] > c['total']:
                    dados['contas_fixas'].pop(i)
                salvar_dados(dados)
                st.rerun()
            
            if col_p2.button("Excluir", key=f"del_c_{i}"):
                dados['contas_fixas'].pop(i)
                salvar_dados(dados)
                st.rerun()

        st.divider()

        # --- GASTOS DIÁRIOS ---
        st.subheader("🛍️ Lançar Gasto Avulso")
        g_d = st.text_input("O que comprou?")
        g_v = st.number_input("Valor R$", min_value=0.0, key="gv_avulso")
        if st.button("LANÇAR GASTO"):
            if g_d and g_v > 0:
                dados['gastos_diarios'].append({"desc": g_d, "valor": g_v})
                salvar_dados(dados)
                st.rerun()
        
        with st.expander("Ver Histórico de Gastos"):
            for idx, g in enumerate(reversed(dados['gastos_diarios'])):
                st.write(f"• {g['desc']}: R$ {g['valor']:.2f}")
                if st.button("Estornar", key=f"st_{idx}"):
                    dados['gastos_diarios'].remove(g)
                    salvar_dados(dados)
                    st.rerun()

    with tab2:
        st.subheader("💰 Patrimônio Acumulado")
        st.title(f"R$ {dados['patrimonio']:.2f}")
        # (Restante do código de metas mantido...)
        for i, m in enumerate(dados['metas']):
            prog = min(dados['patrimonio'] / m['alvo'], 1.0) if m['alvo'] > 0 else 0
            st.write(f"**{m['nome']}**")
            st.progress(prog)
            st.write(f"R$ {dados['patrimonio']:.2f} de R$ {m['alvo']:.2f}")

    with tab3:
        if st.sidebar.button("Log Out"):
            st.session_state["autenticado"] = False
            st.rerun()
        if st.button("Zerar Aplicativo (CUIDADO)"):
            dados = {"patrimonio": 0.0, "gastos_diarios": [], "contas_fixas": [], "metas": [], "salario": 0.0, "extra": 0.0, "pct": 10.0}
            salvar_dados(dados)
            st.rerun()
