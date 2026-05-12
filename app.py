import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt # Adicionado conforme solicitado
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

# --- FUNÇÕES DE DADOS ---
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

# --- DASHBOARD ---
st.markdown("<h1 style='text-align: center;'>📱 Financeiro Pro</h1>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("Saldo Livre", formatar_br(saldo_livre))
c2.metric("Total CDB", formatar_br(dados['cdb_total']))
c3.metric("Total Tesouro", formatar_br(dados['tesouro_total']))

tab1, tab2, tab3, tab4 = st.tabs(["💰 Fluxo", "🎯 Investimentos", "📝 Contas", "📊 Extrato"])

with tab1:
    with st.container(border=True):
        st.subheader("🛒 Registrar Gasto")
        g_n = st.text_input("Descrição")
        g_v = st.number_input("Valor R$", min_value=0.0, format="%.2f")
        g_c = st.selectbox("Categoria", ["Alimentação", "Transporte", "Lazer", "Saúde", "Casa", "Outros"])
        
        # Substituição do messagebox.askyesno (Versão Web)
        with st.popover("Confirmar Lançamento", use_container_width=True):
            st.write(f"Deseja confirmar o pagamento de {g_n}?")
            if st.button("Sim, Processar Pagamento"):
                if g_n and g_v > 0:
                    dados['gastos_diarios'].append({
                        "data": datetime.now().strftime("%d/%m/%Y"),
                        "desc": g_n, "valor": g_v, "cat": g_c
                    })
                    salvar_dados(dados)
                    st.success("Pagamento Processado")
                    st.rerun()

with tab3:
    st.subheader("📅 Parcelas")
    # Interface para exibir como uma tabela organizada (Similar ao Treeview solicitado)
    if dados['contas_fixas']:
        for i, c in enumerate(dados['contas_fixas']):
            with st.container(border=True):
                col_t1, col_t2 = st.columns([3, 1])
                col_t1.write(f"**{c['nome']}** | {c['atual']}/{c['total']}")
                # Botão de confirmação de pagamento de título
                with col_t2.popover("Pagar"):
                    st.write("Confirmar título?")
                    if st.button("Confirmar", key=f"p_{i}"):
                        dados['gastos_diarios'].append({"data": datetime.now().strftime("%d/%m/%Y"), "desc": f"Título: {c['nome']}", "valor": c['valor'], "cat": "Fixo"})
                        c['atual'] += 1
                        if c['atual'] > c['total']: dados['contas_fixas'].pop(i)
                        salvar_dados(dados)
                        st.rerun()

with tab4:
    st.subheader("📊 Análise Mensal")
    
    if dados['gastos_diarios']:
        # LÓGICA DO MATPLOTLIB (Conforme seu pedido)
        df = pd.DataFrame(dados['gastos_diarios'])
        resumo = df.groupby('cat')['valor'].sum()
        
        labels = resumo.index.tolist()
        valores = resumo.values.tolist()

        fig, ax = plt.subplots(figsize=(6, 4), subplot_kw=dict(aspect="equal"))
        fig.patch.set_facecolor('#0d1117') # Cor de fundo igual ao app
        
        # Gráfico Donut solicitado
        ax.pie(valores, labels=labels, autopct='%1.1f%%', startangle=140, 
               colors=['#3498db', '#e74c3c', '#2ecc71', '#f1c40f', '#9b59b6'], 
               wedgeprops=dict(width=0.4), textprops={'color':"w"})
        
        plt.title("Distribuição Mensal", fontsize=12, pad=20, color="w")
        st.pyplot(fig) # Comando para exibir o gráfico do Matplotlib no Streamlit

        st.divider()
        st.write("### 📜 Histórico de Lançamentos")
        # Exibição de tabela (Substituindo o Treeview por algo nativo do Streamlit)
        df_visu = df.tail(10)[::-1].copy()
        df_visu = df_visu[['data', 'desc', 'valor']] # Seleciona colunas solicitadas
        df_visu['valor'] = df_visu['valor'].apply(formatar_br)
        
        st.dataframe(df_visu, use_container_width=True, hide_index=True)
    else:
        st.info("Sem dados para exibir o gráfico.")
