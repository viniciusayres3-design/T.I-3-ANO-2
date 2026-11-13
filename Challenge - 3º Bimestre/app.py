
import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Portal Web de Helpdesk", page_icon="🛠️", layout="wide")

conexao = sqlite3.connect("helpdesk.db", check_same_thread=False)
cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS chamados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descricao TEXT NOT NULL,
    prioridade TEXT NOT NULL,
    status TEXT NOT NULL
)
""")
conexao.commit()

st.title("Portal Web de Helpdesk")
st.write("Sistema para abertura e gerenciamento de chamados técnicos.")

st.subheader("Abrir novo chamado")
titulo = st.text_input("Título")
descricao = st.text_area("Descrição")
prioridade = st.selectbox("Prioridade", ["Baixa", "Média", "Alta"])

if st.button("Cadastrar chamado", type="primary"):
    if titulo.strip() and descricao.strip():
        cursor.execute(
            "INSERT INTO chamados (titulo, descricao, prioridade, status) VALUES (?, ?, ?, ?)",
            (titulo.strip(), descricao.strip(), prioridade, "Aberto"),
        )
        conexao.commit()
        st.success("Chamado cadastrado com sucesso!")
        st.rerun()
    else:
        st.warning("Preencha o título e a descrição.")

st.divider()
st.subheader("Chamados cadastrados")

df = pd.read_sql_query("SELECT * FROM chamados ORDER BY id DESC", conexao)

if df.empty:
    st.info("Nenhum chamado cadastrado.")
else:
    df["Excluir"] = False

    st.data_editor(
        df,
        hide_index=True,
        disabled=["id", "titulo", "descricao", "prioridade"],
        column_config={
            "id": st.column_config.NumberColumn("ID"),
            "titulo": st.column_config.TextColumn("Título"),
            "descricao": st.column_config.TextColumn("Descrição"),
            "prioridade": st.column_config.TextColumn("Prioridade"),
            "status": st.column_config.SelectboxColumn(
                "Status",
                options=["Aberto", "Em andamento", "Resolvido"],
                required=True,
            ),
            "Excluir": st.column_config.CheckboxColumn("Excluir"),
        },
        key="tabela_chamados",
        use_container_width=True,
    )

    if st.button("Salvar alterações"):
        alteracoes = st.session_state["tabela_chamados"].get("edited_rows", {})

        for linha, dados in alteracoes.items():
            id_chamado = int(df.iloc[int(linha)]["id"])

            if "status" in dados:
                cursor.execute(
                    "UPDATE chamados SET status = ? WHERE id = ?",
                    (dados["status"], id_chamado),
                )

            if dados.get("Excluir") is True:
                cursor.execute("DELETE FROM chamados WHERE id = ?", (id_chamado,))

        conexao.commit()
        st.success("Alterações salvas!")
        st.rerun()

conexao.close()
