
import streamlit as st
from st_paywall import add_auth

from states import initialize_session_state
from agents import run_agent
from graph import display_graph


# Definir o layout da página como centralizado
st.set_page_config(
                    # layout="wide",
                   page_title="3Knowledge 🌳🧠",
                   page_icon="🌳🧠")

initialize_session_state()

def main():

    col1, col2 = st.columns(2, gap="small", vertical_alignment="center")
    with col1:
        try:
            st.image("C:\\Users\\Marcos Vinicius\\Documents\\Notebooks\\Project 1\\project-1\\images\\logo_1.png", width=300)
        except:
            st.image("./images/logo_1.png", width=300) 

    with col2:
        st.title("Sua árvore de conhecimento! 🌳🧠", anchor=False)
        st.write(
            "Pesquias ramificadas e inteligentes, ageregando infomações de diversas fonte."
        )


    add_auth(required=True,
        login_button_text="Login com Google",
        login_button_color="#FD504D",
        login_sidebar=False)
    

    if st.session_state['user_subscribed'] == True:
        if not st.session_state['search_query']:
            st.header("Árvore de Conhecimento 🌳🧠")
        else:
            st.header(f"🌳 {st.session_state['search_query']} 🧠")    

        with st.sidebar:
            st.header("Pesquisa:")
            st.session_state['search_query'] = st.text_input("Tema principal 📚🔎", "")
            search_button = st.button("Mapa Mental 🗺️🧠")

            if search_button and st.session_state['search_query']:
                # Executar busca na Wikipedia e o LLM
                run_agent()

            # Exibir o histórico de pesquisas como botões
            if st.session_state['response_history']:
                st.subheader("Histórico de Pesquisas")
                for i, entry in enumerate(st.session_state['response_history']):
                    query_label = entry['query']
                    if st.button(query_label, key=f'history_{i}'):
                        st.session_state['nodes_data'] = entry['response']['nodes']
                        st.session_state['edges_data'] = entry['response']['edges']
                        st.session_state['response'] = entry['response']
                        st.session_state['search_query'] = query_label

            st.write(f"Subscription Status: {st.session_state.user_subscribed}")
            st.write("🎉 Otimo! Você é um usuário Premium! 🎉")
            st.write(f'Usuario: {st.session_state.email}')

        # Exibir o gráfico
        with st.container(border=True):
            display_graph()

        # Exibir conteúdo da Wikipedia
        if st.session_state['wiki_content']:
            st.subheader(f"Conteúdo da Wikipedia para: {st.session_state['search_query']}")
            st.write(st.session_state['wiki_content'])


if __name__ == "__main__":
    main()
