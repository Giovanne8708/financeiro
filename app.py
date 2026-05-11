import streamlit as st
import json
import os

# --- CONFIGURAÇÕES DE ACESSO ---
USUARIO_CORRETO = "giovanne"
SENHA_CORRETA = "8708" 

st.set_page_config(page_title="Status Fluxo Pro", layout="centered")

# Estilo Visual Mobile
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; height: 3.5em; }
    .stMetric { background-color: #0e1117; padding: 10px; border-radius: 10px; border: 1px solid #30363d; }
    .conta-card { background-color: #161b22; padding: 10px; border-radius: 8px; border-left: 5px solid #00ff00; margin-bottom: 10px; }
    .quinzena-header { color: #feb236; font-size: 20px; font-weight: bold; text-align: center; margin-bottom: 15px; border: 1px solid #feb236; padding: 5px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

def format_num(valor):
    if isinstance(valor, str):
        valor = valor.replace(',', '.')
    try:
        return float(valor)
    except:
        return 0.0

def carregar_dados():
    if os.path.exists("dados.json"):
        with open("dados.json", "r") as f:
            d = json.load(f)
            # CORREÇÃO DO ERRO: Garante que todas as chaves novas existam
            if "quinzena" not in d: d["quinzena"] = "1ª Quinzena"
            if "salario" not in d: d["salario"] = 0.0
            if "extra" not in d: d["extra"] = 0.0
            if "pct" not in d: d["pct"] = 10.0
            return d
    return {"patrimonio": 0.0, "gastos_diarios": [], "contas_fixas": [], "metas": [], "salario": 0.0, "extra": 0.0, "pct": 10.0, "quinzena": "1ª Quinzena"}

def salvar_dados(dados):
    with open("dados.json", "w") as f:
        json.dump(dados, f, indent=4)

def verificar_login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False
    if not st.session_state["autenticado"]:
        st.title("🔐 Acesso Quinzenal")
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

if verificar_login():
    dados = carregar_dados()

    st.title("📊 Controle Quinzenal")
    
    tab1, tab2, tab3 = st.tabs(["💰 Fluxo Atual", "🎯 Metas", "⚙️ Virar Quinzena"])

    with tab1:
        # Pega a quinzena de forma segura
        q_label = dados.get("quinzena", "1ª Quinzena")
        st.markdown(f"<div class='quinzena-header'>{q_label}</div>", unsafe_allow_html=True)
        
        col_s, col_e, col_p = st.columns(3)
        sal_txt = col_s.text_input("Recebido (Q)", value=str(dados.get("salario", 0.0)))
        ext_txt = col_e.text_input("Extra (Q)", value=str(dados.get("extra", 0.0)))
        pct_txt = col_p.text_input("Meta %", value=str(dados.get("pct", 10.0)))
        
        salario = format_num(sal_txt)
        extra = format_num(ext_txt)
        pct = format_num(pct_txt)
        
        if salario != dados["salario"] or extra != dados["extra"] or pct != dados["pct"]:
            dados.update({"salario": salario, "extra": extra, "pct": pct})
            salvar_dados(dados)

        total_gastos = sum(g['valor'] for g in dados['gastos_diarios'])
        saldo_livre = (salario + extra) - total_gastos
        aporte_sugerido = ((salario + extra) * (pct / 100)) / 2
        
        st.metric("SALDO DISPONÍVEL", f"R$ {saldo_livre:.2f}")

        st.subheader("🏦 Guardar Investimento")
        c1, c2 = st.columns(2)
        with c1:
            if st.button(f"CDB: R$ {aporte_sugerido:.2f}"):
                dados['patrimonio'] += aporte_sugerido
                dados['gastos_diarios'].append({"desc": f"Inv: CDB ({q_label})", "valor": aporte_sugerido})
                salvar_dados(dados)
                st.rerun()
        with c2:
            if st.button(f"TESOURO: R$ {aporte_sugerido:.2f}"):
                dados['patrimonio'] += aporte_sugerido
                dados['gastos_diarios'].append({"desc": f"Inv: Tesouro ({q_label})", "valor": aporte_sugerido})
                salvar_dados(dados)
                st.rerun()

        st.divider()
        st.subheader("🛍️ Lançar Gasto")
        g_d = st.text_input("Descrição")
        g_v_txt = st.text_input("Valor R$", key="gv_fix")
        if st.button("LANÇAR AGORA"):
            g_v = format_num(g_v_txt)
            if g_d and g_v > 0:
                dados['gastos_diarios'].append({"desc": g_d, "valor": g_v})
                salvar_dados(dados)
                st.rerun()

    with tab2:
        st.subheader("💰 Patrimônio Total")
        st.title(f"R$ {dados['patrimonio']:.2f}")
        st.divider()
        with st.expander("+ Novo Objetivo"):
            m_n = st.text_input("Meta")
            m_v_t = st.text_input("Alvo R$", key="meta_txt")
            if st.button("Salvar Meta"):
                m_v = format_num(m_v_t)
                dados['metas'].append({"nome": m_n, "alvo": m_v})
                salvar_dados(dados)
                st.rerun()
        for i, m in enumerate(dados['metas']):
            p = min(dados['patrimonio'] / m['alvo'], 1.0) if m['alvo'] > 0 else 0
            st.write(f"**{m['nome']}**")
            st.progress(p)
            if st.button("Excluir", key=f"dm_{i}"):
                dados['metas'].pop(i)
                salvar_dados(dados)
                st.rerun()

    with tab3:
        st.subheader("🔄 Virada de Quinzena")
        st.write(f"Saldo para transportar: **R$ {saldo_livre:.2f}**")
        if st.button("FINALIZAR E TRANSPORTAR"):
            dados["extra"] = saldo_livre
            dados["salario"] = 0.0
            dados["gastos_diarios"] = []
            dados["quinzena"] = "2ª Quinzena" if dados.get("quinzena") == "1ª Quinzena" else "1ª Quinzena"
            salvar_dados(dados)
            st.success("Pronto! Saldo transportado.")
            st.rerun()
