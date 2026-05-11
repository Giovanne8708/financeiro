import streamlit as st
import json
import os

# --- CONFIGURAÇÕES DE ACESSO ---
USUARIO_CORRETO = "giovanne"
SENHA_CORRETA = "8708" 

st.set_page_config(page_title="Status Fluxo", layout="centered")

# Estilo visual para Mobile
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .stMetric { background-color: #0e1117; padding: 10px; border-radius: 10px; border: 1px solid #30363d; }
    .conta-card { background-color: #161b22; padding: 10px; border-radius: 8px; border-left: 5px solid #58a6ff; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Função para aceitar vírgula ou ponto
def format_num(valor):
    if isinstance(valor, str):
        valor = valor.replace(',', '.')
    try:
        return float(valor)
    except:
        return 0.0

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

    tab1, tab2, tab3 = st.tabs(["💰 Fluxo e Pagamentos", "🎯 Metas e Patrimônio", "⚙️ Ajustes"])

    with tab1:
        # --- ENTRADAS (Tratando Vírgula e Ponto) ---
        col_s, col_e, col_p = st.columns(3)
        
        # Usamos text_input para permitir que o usuário digite a vírgula livremente
        sal_txt = col_s.text_input("Salário", value=str(dados.get("salario", 0.0)))
        ext_txt = col_e.text_input("Extra", value=str(dados.get("extra", 0.0)))
        pct_txt = col_p.text_input("Meta %", value=str(dados.get("pct", 10.0)))
        
        salario = format_num(sal_txt)
        extra = format_num(ext_txt)
        pct = format_num(pct_txt)
        
        if salario != dados["salario"] or extra != dados["extra"] or pct != dados["pct"]:
            dados.update({"salario": salario, "extra": extra, "pct": pct})
            salvar_dados(dados)

        aporte_sugerido = ((salario + extra) * (pct / 100)) / 2
        total_saidas = sum(g['valor'] for g in dados['gastos_diarios'])
        saldo_livre = (salario + extra) - total_saidas
        
        st.metric("SALDO LIVRE", f"R$ {saldo_livre:.2f}")

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
        with st.expander("+ Adicionar Conta"):
            n_c = st.text_input("Nome da Conta")
            v_c_txt = st.text_input("Valor da Parcela R$")
            p_a = st.number_input("Parcela Atual", min_value=1, value=1)
            p_t = st.number_input("Total de Parcelas", min_value=1, value=1)
            
            if st.button("Salvar Conta"):
                v_c = format_num(v_c_txt)
                if n_c and v_c > 0:
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
                dados['gastos_diarios'].append({"desc": f"Pago: {c['nome']} ({c['atual']}/{c['total']})", "valor": c['valor']})
                c['atual'] += 1
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
        st.subheader("🛍️ Lançar Gasto")
        g_d = st.text_input("Descrição")
        g_v_txt = st.text_input("Valor R$", key="gv_txt")
        if st.button("LANÇAR GASTO"):
            g_v = format_num(g_v_txt)
            if g_d and g_v > 0:
                dados['gastos_diarios'].append({"desc": g_d, "valor": g_v})
                salvar_dados(dados)
                st.rerun()

    with tab2:
        st.subheader("💰 Patrimônio Acumulado")
        st.title(f"R$ {dados['patrimonio']:.2f}")
        
        st.divider()
        st.subheader("🎯 Suas Metas")
        with st.expander("+ Novo Objetivo"):
            m_n = st.text_input("Nome do Objetivo")
            m_v_txt = st.text_input("Valor Alvo R$")
            if st.button("Salvar Meta"):
                m_v = format_num(m_v_txt)
                if m_n and m_v > 0:
                    dados['metas'].append({"nome": m_n, "alvo": m_v})
                    salvar_dados(dados)
                    st.rerun()

        for i, m in enumerate(dados['metas']):
            prog = min(dados['patrimonio'] / m['alvo'], 1.0) if m['alvo'] > 0 else 0
            st.write(f"**{m['nome']}**")
            st.progress(prog)
            st.write(f"R$ {dados['patrimonio']:.2f} de R$ {m['alvo']:.2f}")
            if st.button("Excluir Meta", key=f"del_m_{i}"):
                dados['metas'].pop(i)
                salvar_dados(dados)
                st.rerun()

    with tab3:
        if st.sidebar.button("Log Out"):
            st.session_state["autenticado"] = False
            st.rerun()
        if st.button("Zerar Aplicativo"):
            if st.checkbox("Confirmar reset total?"):
                dados = {"patrimonio": 0.0, "gastos_diarios": [], "contas_fixas": [], "metas": [], "salario": 0.0, "extra": 0.0, "pct": 10.0}
                salvar_dados(dados)
                st.rerun()
