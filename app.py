import streamlit as st
import json
import os

# --- CONFIGURAÇÕES DE ACESSO ---
USUARIO_CORRETO = "giovanne"
SENHA_CORRETA = "8708" 

st.set_page_config(page_title="Financeiro", layout="centered")

# Estilo Visual Moderno
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; height: 3.5em; }
    .stMetric { background-color: #0e1117; padding: 10px; border-radius: 10px; border: 1px solid #30363d; }
    .conta-card { background-color: #161b22; padding: 15px; border-radius: 10px; border-left: 5px solid #00ff00; margin-bottom: 15px; border: 1px solid #30363d; }
    .meta-card { background-color: #111827; padding: 15px; border-radius: 12px; border: 1px solid #374151; margin-bottom: 15px; }
    .quinzena-header { color: #feb236; font-size: 22px; font-weight: bold; text-align: center; margin-bottom: 15px; border: 2px solid #feb236; padding: 8px; border-radius: 10px; background-color: rgba(254, 178, 54, 0.1); }
    h3 { color: #58a6ff !important; }
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
            # Garante que chaves existam para evitar erros de versão
            chaves = {"quinzena": "1ª Quinzena", "salario": 0.0, "extra": 0.0, "pct": 10.0, 
                      "contas_fixas": [], "gastos_diarios": [], "metas": [], "patrimonio": 0.0}
            for k, v in chaves.items():
                if k not in d: d[k] = v
            return d
    return {"patrimonio": 0.0, "gastos_diarios": [], "contas_fixas": [], "metas": [], "salario": 0.0, "extra": 0.0, "pct": 10.0, "quinzena": "1ª Quinzena"}

def salvar_dados(dados):
    with open("dados.json", "w") as f:
        json.dump(dados, f, indent=4)

def verificar_login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False
    if not st.session_state["autenticado"]:
        st.title("🔐 Login Financeifinanceiro")
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

    st.title("📱 Financeifinanceiro")
    
    tab1, tab2, tab3 = st.tabs(["💰 Meu Fluxo", "🎯 Minhas Metas", "⚙️ Sistema"])

    with tab1:
        q_label = dados.get("quinzena", "1ª Quinzena")
        st.markdown(f"<div class='quinzena-header'>{q_label}</div>", unsafe_allow_html=True)
        
        # --- ENTRADAS ---
        col_s, col_e, col_p = st.columns(3)
        sal_txt = col_s.text_input("Recebido", value=str(dados["salario"]))
        ext_txt = col_e.text_input("Extra", value=str(dados["extra"]))
        pct_txt = col_p.text_input("Meta %", value=str(dados["pct"]))
        
        salario, extra, pct = format_num(sal_txt), format_num(ext_txt), format_num(pct_txt)
        
        if (salario, extra, pct) != (dados["salario"], dados["extra"], dados["pct"]):
            dados.update({"salario": salario, "extra": extra, "pct": pct})
            salvar_dados(dados)

        total_gastos = sum(g['valor'] for g in dados['gastos_diarios'])
        saldo_livre = (salario + extra) - total_gastos
        aporte_sugerido = ((salario + extra) * (pct / 100)) / 2
        
        st.metric("SALDO DISPONÍVEL", f"R$ {saldo_livre:.2f}")

        # --- INVESTIMENTOS ---
        st.subheader("🏦 Guardar Agora")
        c1, c2 = st.columns(2)
        with c1:
            if st.button(f"CDB\n R$ {aporte_sugerido:.2f}"):
                dados['patrimonio'] += aporte_sugerido
                dados['gastos_diarios'].append({"desc": f"Inv: CDB ({q_label})", "valor": aporte_sugerido})
                salvar_dados(dados)
                st.rerun()
        with c2:
            if st.button(f"TESOURO\n R$ {aporte_sugerido:.2f}"):
                dados['patrimonio'] += aporte_sugerido
                dados['gastos_diarios'].append({"desc": f"Inv: Tesouro ({q_label})", "valor": aporte_sugerido})
                salvar_dados(dados)
                st.rerun()

        st.divider()

        # --- CONTAS FIXAS ---
        st.subheader("📝 Contas e Parcelas")
        with st.expander("+ Adicionar Conta"):
            n_c = st.text_input("Nome da Conta")
            v_c_txt = st.text_input("Valor da Parcela")
            p_a = st.number_input("Parcela Atual", min_value=1, value=1)
            p_t = st.number_input("Total de Parcelas", min_value=1, value=1)
            if st.button("Salvar Conta"):
                v_c = format_num(v_c_txt)
                if n_c and v_c > 0:
                    dados['contas_fixas'].append({"nome": n_c, "valor": v_c, "atual": p_a, "total": p_t})
                    salvar_dados(dados)
                    st.rerun()

        for i, c in enumerate(dados['contas_fixas']):
            st.markdown(f"<div class='conta-card'><b>{c['nome']}</b><br>Parcela {c['atual']}/{c['total']} | R$ {c['valor']:.2f}</div>", unsafe_allow_html=True)
            col_p1, col_p2 = st.columns(2)
            if col_p1.button(f"PAGAR", key=f"pay_{i}"):
                dados['gastos_diarios'].append({"desc": f"Pago: {c['nome']} ({c['atual']}/{c['total']})", "valor": c['valor']})
                c['atual'] += 1
                if c['atual'] > c['total']: dados['contas_fixas'].pop(i)
                salvar_dados(dados)
                st.rerun()
            if col_p2.button("X", key=f"del_c_{i}"):
                dados['contas_fixas'].pop(i)
                salvar_dados(dados)
                st.rerun()

        st.divider()
        st.subheader("🛍️ Lançar Gasto")
        g_d = st.text_input("O que comprou?")
        g_v_txt = st.text_input("Valor R$", key="gv_main")
        if st.button("Lançar Gasto"):
            g_v = format_num(g_v_txt)
            if g_d and g_v > 0:
                dados['gastos_diarios'].append({"desc": g_d, "valor": g_v})
                salvar_dados(dados)
                st.rerun()

    with tab2:
        st.markdown("<h2 style='text-align: center;'>🎯 Metas e Objetivos</h2>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center; font-size: 20px;'>Patrimônio Total: <b>R$ {dados['patrimonio']:.2f}</b></div>", unsafe_allow_html=True)
        st.divider()

        with st.expander("+ Criar Novo Objetivo"):
            m_n = st.text_input("Qual o seu objetivo?")
            m_v_t = st.text_input("Quanto precisa (R$)?", key="m_val_txt")
            if st.button("Criar Meta"):
                m_v = format_num(m_v_t)
                if m_n and m_v > 0:
                    dados['metas'].append({"nome": m_n, "alvo": m_v})
                    salvar_dados(dados)
                    st.rerun()

        for i, m in enumerate(dados['metas']):
            porcentagem = min(dados['patrimonio'] / m['alvo'], 1.0) if m['alvo'] > 0 else 0
            resta = max(m['alvo'] - dados['patrimonio'], 0)
            
            st.markdown(f"""
            <div class='meta-card'>
                <div style='display: flex; justify-content: space-between;'>
                    <b>{m['nome']}</b>
                    <span>{porcentagem*100:.1f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(porcentagem)
            st.caption(f"Faltam R$ {resta:.2f} para atingir R$ {m['alvo']:.2f}")
            if st.button(f"Remover {m['nome']}", key=f"rm_{i}"):
                dados['metas'].pop(i)
                salvar_dados(dados)
                st.rerun()

    with tab3:
        st.subheader("🔄 Controle de Quinzena")
        st.write(f"Saldo para levar: **R$ {saldo_livre:.2f}**")
        if st.button("FECHAR QUINZENA E LEVAR SALDO"):
            dados["extra"] = saldo_livre
            dados["salario"] = 0.0
            dados["gastos_diarios"] = []
            dados["quinzena"] = "2ª Quinzena" if dados.get("quinzena") == "1ª Quinzena" else "1ª Quinzena"
            salvar_dados(dados)
            st.rerun()

        st.divider()
        st.subheader("🚨 Zona de Perigo")
        if st.button("RESET TOTAL DE DADOS"):
            if st.checkbox("Eu tenho certeza que quero apagar TUDO"):
                if os.path.exists("dados.json"):
                    os.remove("dados.json")
                st.warning("Todos os dados foram apagados. Recarregando...")
                st.rerun()
        
        if st.sidebar.button("Logout"):
            st.session_state["autenticado"] = False
            st.rerun()
