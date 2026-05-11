import streamlit as st
import json
import os

# --- CONFIGURAÇÕES DE SEGURANÇA ---
# Defina aqui seu usuário e senha desejados
USUARIO_CORRETO = "giovanne"
SENHA_CORRETA = "8708" # Troque por uma senha segura!

def verificar_login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.title("🔐 Acesso Restrito")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        
        if st.button("Entrar"):
            if usuario == USUARIO_CORRETO and senha == SENHA_CORRETA:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos")
        return False
    return True

# --- LOGICA DE DADOS ---
def carregar_dados():
    if os.path.exists("dados.json"):
        with open("dados.json", "r") as f:
            return json.load(f)
    return {"patrimonio": 0.0, "gastos": [], "metas": []}

def salvar_dados(dados):
    with open("dados.json", "w") as f:
        json.dump(dados, f, indent=4)

# --- INÍCIO DO APP ---
if verificar_login():
    # Só roda se o login estiver correto
    dados = carregar_dados()

    st.title("📦 Status Fluxo Mobile")
    
    # Sidebar para Logout
    if st.sidebar.button("Sair / Bloquear"):
        st.session_state["autenticado"] = False
        st.rerun()

    # --- ABAS DO SISTEMA ---
    tab1, tab2, tab3 = st.tabs(["💰 Fluxo", "🎯 Metas", "📜 Histórico"])

    with tab1:
        st.subheader("Entradas")
        col1, col2 = st.columns(2)
        salario = col1.number_input("Salário", value=0.0)
        extra = col2.number_input("Extra", value=0.0)
        
        gastos_total = sum(g['valor'] for g in dados['gastos'])
        saldo_livre = (salario + extra) - gastos_total
        
        st.metric("Saldo Livre", f"R$ {saldo_livre:.2f}", delta_color="normal")

        st.divider()
        st.subheader("Investir / Guardar")
        local = st.text_input("Local do Investimento", placeholder="Ex: CDB Safra")
        valor_inv = st.number_input("Valor para Guardar", min_value=0.0)
        
        if st.button("Confirmar Aporte"):
            if local and valor_inv > 0:
                dados['patrimonio'] += valor_inv
                dados['gastos'].append({"desc": f"Guardou em: {local}", "valor": valor_inv})
                salvar_dados(dados)
                st.success("Valor guardado com sucesso!")
                st.rerun()

    with tab2:
        st.subheader("Minhas Metas")
        n_meta = st.text_input("Nome da Meta")
        v_meta = st.number_input("Valor Alvo", min_value=0.0)
        
        if st.button("Criar Meta"):
            if n_meta and v_meta > 0:
                dados['metas'].append({"nome": n_meta, "alvo": v_meta})
                salvar_dados(dados)
                st.rerun()
        
        st.divider()
        for i, m in enumerate(dados['metas']):
            prog = min(dados['patrimonio'] / m['alvo'], 1.0) if m['alvo'] > 0 else 0
            st.write(f"**{m['nome']}**")
            st.progress(prog)
            st.caption(f"Progresso: {prog*100:.1f}% | Falta: R$ {max(0.0, m['alvo']-dados['patrimonio']):.2f}")

    with tab3:
        st.subheader("Últimas Movimentações")
        if dados['gastos']:
            for g in reversed(dados['gastos']):
                st.write(f"• {g['desc']}: R$ {g['valor']:.2f}")
        else:
            st.info("Nenhum gasto ou aporte registrado.")