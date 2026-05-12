import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÕES DO APP ---
st.set_page_config(page_title="Financeiro Pro", layout="centered", page_icon="💰")

# --- CSS AVANÇADO (DESIGN E ESPAÇAMENTO) ---
st.markdown("""
    <style>
    /* Fundo e Container */
    .main { background-color: #0d1117; }
    
    /* Cards Estilizados */
    .section-card {
        background-color: #161b22;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #30363d;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Títulos e Labels */
    h1, h2, h3 { color: #58a6ff !important; font-family: 'Segoe UI', sans-serif; }
    .stMetric { background-color: #1f2937 !important; border-radius: 12px; padding: 15px !important; }
    
    /* Botões */
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s;
        border: none;
    }
    
    /* Customização de Input */
    .stTextInput>div>div>input { background-color: #0d1117 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE SISTEMA ---
def format_num(valor):
    if isinstance(valor, str):
        # Remove R$, espaços e pontos de milhar, troca vírgula por ponto
        valor = valor.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
    try:
        return float(valor)
    except:
        return 0.0

def carregar_dados():
    modelo = {"patrimonio": 0.0, "gastos_diarios": [], "contas_fixas": [], "metas": [], "salario": 0.0, "extra": 0.0, "pct": 10.0, "quinzena": "1ª Quinzena"}
    if os.path.exists("dados.json"):
        with open("dados.json", "r") as f:
            d = json.load(f)
            for k, v in modelo.items():
                if k not in d: d[k] = v
            return d
    return modelo

def salvar_dados(dados):
    with open("dados.json", "w") as f:
        json.dump(dados, f, indent=4)

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>🔐 Financeiro</h1>", unsafe_allow_html=True)
    with st.container():
        u = st.text_input("Usuário")
        s = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if u == "giovanne" and s == "8708":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")
    st.stop()

# --- INÍCIO DO APP ---
dados = carregar_dados()

# Sidebar para Logout e Reset
with st.sidebar:
    st.title("⚙️ Opções")
    if st.button("Sair do Sistema"):
        st.session_state.autenticado = False
        st.rerun()
    
    st.divider()
    st.subheader("🚨 Zona de Perigo")
    if st.checkbox("Confirmar Reset Total"):
        if st.button("APAGAR TODOS OS DADOS"):
            dados = {"patrimonio": 0.0, "gastos_diarios": [], "contas_fixas": [], "metas": [], "salario": 0.0, "extra": 0.0, "pct": 10.0, "quinzena": "1ª Quinzena"}
            salvar_dados(dados)
            st.warning("Dados apagados!")
            st.rerun()

# Título Principal com Respiro
st.markdown(f"<h1 style='text-align: center;'>📊 Financeiro Pro</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #8b949e;'>Gerenciando: {dados['quinzena']}</p>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["💰 Fluxo & Gastos", "🎯 Metas de Longo Prazo", "📈 Análise"])

with tab1:
    # --- CARD DE RENDA ---
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        novo_sal = st.text_input("Recebido", value=f"{dados['salario']:.2f}")
    with col2:
        novo_ext = st.text_input("Extra", value=f"{dados['extra']:.2f}")
    with col3:
        nova_pct = st.text_input("Meta %", value=f"{dados['pct']:.1f}")
    
    # Atualização automática ao mudar valor
    val_sal, val_ext, val_pct = format_num(novo_sal), format_num(novo_ext), format_num(nova_pct)
    if (val_sal, val_ext, val_pct) != (dados['salario'], dados['extra'], dados['pct']):
        dados.update({"salario": val_sal, "extra": val_ext, "pct": val_pct})
        salvar_dados(dados)
    st.markdown("</div>", unsafe_allow_html=True)

    # --- MÉTRICAS DE DESTAQUE ---
    total_gastos = sum(g['valor'] for g in dados['gastos_diarios'])
    saldo_livre = (val_sal + val_ext) - total_gastos
    aporte = ((val_sal + val_ext) * (val_pct / 100)) / 2
    
    c_met1, c_met2 = st.columns(2)
    c_met1.metric("DISPONÍVEL AGORA", saldo_formatado, delta=f"R$ {val_sal+val_ext:.2f} Total")
    c_met2.metric("INVESTIMENTO (Q)", f"R$ {aporte:.2f}", delta_color="normal")

    # --- CARD DE INVESTIR ---
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("🏦 Guardar Investimento")
    ci1, ci2 = st.columns(2)
    if ci1.button(f"INVESTIR CDB (R$ {aporte:.2f})"):
        dados['patrimonio'] += aporte
        dados['gastos_diarios'].append({"desc": "Investimento CDB", "valor": aporte, "cat": "Investimento"})
        salvar_dados(dados)
        st.success("CDB Aplicado!")
        st.rerun()
    if ci2.button(f"INVESTIR TESOURO (R$ {aporte:.2f})"):
        dados['patrimonio'] += aporte
        dados['gastos_diarios'].append({"desc": "Investimento Tesouro", "valor": aporte, "cat": "Investimento"})
        salvar_dados(dados)
        st.success("Tesouro Aplicado!")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # --- CONTAS FIXAS ---
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("📝 Contas do Mês")
    with st.expander("+ Cadastrar Nova Parcela/Conta"):
        nome_c = st.text_input("Nome", key="nome_c")
        valor_c = st.text_input("Valor R$", key="val_c")
        col_p1, col_p2 = st.columns(2)
        p_at = col_p1.number_input("Parc. Atual", 1, 100, 1)
        p_to = col_p2.number_input("Parc. Total", 1, 100, 1)
        if st.button("Confirmar Cadastro"):
            v_float = format_num(valor_c)
            if nome_c and v_float > 0:
                dados['contas_fixas'].append({"nome": nome_c, "valor": v_float, "atual": p_at, "total": p_to})
                salvar_dados(dados)
                st.rerun()

    for i, c in enumerate(dados['contas_fixas']):
        col_c1, col_c2, col_c3 = st.columns([2, 1, 1])
        col_c1.markdown(f"**{c['nome']}** ({c['atual']}/{c['total']})")
        col_c2.markdown(f"R$ {c['valor']:.2f}")
        if col_c3.button("PAGAR", key=f"p_{i}"):
            dados['gastos_diarios'].append({"desc": f"Pago: {c['nome']}", "valor": c['valor'], "cat": "Contas Fixas"})
            c['atual'] += 1
            if c['atual'] > c['total']: dados['contas_fixas'].pop(i)
            salvar_dados(dados)
            st.toast(f"{c['nome']} liquidado!", icon="✅")
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # --- LANÇAR GASTO DIÁRIO ---
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("🛒 Lançar Gasto Rápido")
    g_nome = st.text_input("O que comprou?", key="g_nome")
    col_g1, col_g2 = st.columns(2)
    g_valor = col_g1.text_input("Quanto custou? R$", key="g_valor")
    g_cat = col_g2.selectbox("Categoria", ["Alimentação", "Transporte", "Lazer", "Saúde", "Casa", "Outros"])
    
    if st.button("REGISTRAR GASTO"):
        v_g = format_num(g_valor)
        if g_nome and v_g > 0:
            dados['gastos_diarios'].append({"desc": g_nome, "valor": v_g, "cat": g_cat})
            salvar_dados(dados)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<h2 style='text-align: center;'>🎯 Meus Sonhos</h2>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center; font-size: 24px; padding: 10px;'>Patrimônio Acumulado: <b>R$ {dados['patrimonio']:.2f}</b></div>", unsafe_allow_html=True)
    
    with st.expander("+ Adicionar Objetivo"):
        m_nome = st.text_input("Objetivo (Ex: Viagem)")
        m_alvo = st.text_input("Valor necessário R$")
        if st.button("Salvar Objetivo"):
            v_m = format_num(m_alvo)
            if m_nome and v_m > 0:
                dados['metas'].append({"nome": m_nome, "alvo": v_m})
                salvar_dados(dados)
                st.rerun()

    for i, m in enumerate(dados['metas']):
        prog = min(dados['patrimonio'] / m['alvo'], 1.0) if m['alvo'] > 0 else 0
        st.markdown(f"### {m['nome']}")
        st.progress(prog)
        col_m1, col_m2 = st.columns(2)
        col_m1.write(f"Concluído: {prog*100:.1f}%")
        col_m2.write(f"Faltam: R$ {max(m['alvo']-dados['patrimonio'], 0):.2f}")
        if st.button(f"Excluir {m['nome']}", key=f"rm_{i}"):
            dados['metas'].pop(i)
            salvar_dados(dados)
            st.rerun()

with tab3:
    st.subheader("📈 Onde está indo seu dinheiro?")
    if dados['gastos_diarios']:
        df = pd.DataFrame(dados['gastos_diarios'])
        # Gráfico por Categoria
        fig = px.pie(df, values='valor', names='cat', hole=0.4, 
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)
        
        # Lista de Gastos Recentes
        st.subheader("🧾 Histórico desta Quinzena")
        st.dataframe(df[['desc', 'valor', 'cat']], use_container_width=True)
    else:
        st.info("Ainda não há gastos registrados para análise.")

    st.divider()
    if st.button("🔄 VIRAR QUINZENA (Transportar Saldo)"):
        dados["extra"] = saldo_livre
        dados["salario"] = 0.0
        dados["gastos_diarios"] = []
        dados["quinzena"] = "2ª Quinzena" if dados["quinzena"] == "1ª Quinzena" else "1ª Quinzena"
        salvar_dados(dados)
        st.success("Quinzena encerrada! Saldo transportado para Extra.")
        st.rerun()
