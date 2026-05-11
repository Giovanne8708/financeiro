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
            return json.load(f)
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
        st.markdown(f"<div class='quinzena-header'>{dados['quinzena']}</div>", unsafe_allow_html=True)
        
        # --- ENTRADAS (Aceita . e ,) ---
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

        # Cálculos
        renda_total = salario + extra
        total_gastos = sum(g['valor'] for g in dados['gastos_diarios'])
        saldo_livre = renda_total - total_gastos
        aporte_sugerido = (renda_total * (pct / 100)) / 2
        
        st.metric("SALDO DISPONÍVEL", f"R$ {saldo_livre:.2f}")

        # --- BOTÕES DE APORTE ---
        st.subheader("🏦 Guardar Investimento")
        c1, c2 = st.columns(2)
        with c1:
            if st.button(f"CDB: R$ {aporte_sugerido:.2f}"):
                dados['patrimonio'] += aporte_sugerido
                dados['gastos_diarios'].append({"desc": f"Inv: CDB ({dados['quinzena']})", "valor": aporte_sugerido})
                salvar_dados(dados)
                st.rerun()
        with c2:
            if st.button(f"TESOURO: R$ {aporte_sugerido:.2f}"):
                dados['patrimonio'] += aporte_sugerido
                dados['gastos_diarios'].append({"desc": f"Inv: Tesouro ({dados['quinzena']})", "valor": aporte_sugerido})
                salvar_dados(dados)
                st.rerun()

        st.divider()

        # --- CONTAS FIXAS ---
        st.subheader("📝 Contas e Carnês")
        with st.expander("+ Nova Conta"):
            n_c = st.text_input("Item")
            v_c_txt = st.text_input("Valor R$")
            p_a = st.number_input("Parcela Atual", min_value=1, value=1)
            p_t = st.number_input("Total Parcelas", min_value=1, value=1)
            if st.button("Salvar Conta"):
                v_c = format_num(v_c_txt)
                if n_c and v_c > 0:
                    dados['contas_fixas'].append({"nome": n_c, "valor": v_c, "atual": p_a, "total": p_t})
                    salvar_dados(dados)
                    st.rerun()

        for i, c in enumerate(dados['contas_fixas']):
            st.markdown(f"<div class='conta-card'><b>{c['nome']}</b> | {c['atual']}/{c['total']} | R$ {c['valor']:.2f}</div>", unsafe_allow_html=True)
            col_p1, col_p2 = st.columns(2)
            if col_p1.button(f"PAGAR PARCELA", key=f"pay_{i}"):
                dados['gastos_diarios'].append({"desc": f"Pago: {c['nome']} ({c['atual']}/{c['total']})", "valor": c['valor']})
                c['atual'] += 1
                if c['atual'] > c['total']: dados['contas_fixas'].pop(i)
                salvar_dados(dados)
                st.rerun()
            if col_p2.button("Excluir", key=f"del_c_{i}"):
                dados['contas_fixas'].pop(i)
                salvar_dados(dados)
                st.rerun()

        st.divider()

        # --- GASTOS DIÁRIOS ---
        st.subheader("🛍️ Lançar Gasto")
        g_d = st.text_input("Descrição do gasto")
        g_v_txt = st.text_input("Valor R$", key="gv_mobile")
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
        # Seção de Metas (Restaurada)
        with st.expander("+ Novo Objetivo"):
            m_n = st.text_input("Meta")
            m_v_t = st.text_input("Alvo R$")
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
        st.write(f"Saldo atual para transporte: **R$ {saldo_livre:.2f}**")
        
        if st.button("FINALIZAR QUINZENA E TRANSPORTAR SALDO"):
            # 1. Transporta o saldo para o campo Extra
            dados["extra"] = saldo_livre
            # 2. Reseta o salário para você digitar o novo
            dados["salario"] = 0.0
            # 3. Limpa gastos da quinzena que passou
            dados["gastos_diarios"] = []
            # 4. Alterna a quinzena
            dados["quinzena"] = "2ª Quinzena" if dados["quinzena"] == "1ª Quinzena" else "1ª Quinzena"
            
            salvar_dados(dados)
            st.success("Saldo transportado e gastos limpos!")
            st.rerun()

        st.divider()
        if st.sidebar.button("Sair"):
            st.session_state["autenticado"] = False
            st.rerun()
