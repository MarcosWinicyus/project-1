import streamlit as st
from st_paywall import add_auth
from streamlit_agraph import agraph, Node, Edge, Config
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
import json
import re

# Definir o layout da página como centralizado
st.set_page_config(layout="wide",
                   page_title="3Knowledge 🌳🧠", page_icon="🌳🧠")

add_auth(required=True,
         login_button_text="Login with Google",
         login_button_color="#FD504D",
         login_sidebar=False)

# Função para inicializar variáveis de estado
def initialize_session_state():
    if 'nodes_data' not in st.session_state:
        st.session_state['nodes_data'] = None
    if 'edges_data' not in st.session_state:
        st.session_state['edges_data'] = None
    if 'response' not in st.session_state:
        st.session_state['response'] = None
    if 'response_history' not in st.session_state:
        st.session_state['response_history'] = []  # Armazenar respostas anteriores
    if 'search_query' not in st.session_state:
        st.session_state['search_query'] = None

initialize_session_state()

# Função para executar o LLM
def run_ai(query):
    api_key = st.secrets["openai_api_key"]
    if not api_key:
        st.error("API key não encontrada. Por favor, verifique seu arquivo secrets.toml.")
    else:
        # Configurar o LLM da OpenAI com a chave da API
        llm = OpenAI(openai_api_key=api_key,
                     temperature=0,
                     max_tokens=3000)

        # Criar um prompt template
        prompt_template = """
        Você é um especialista em criação de mapas mentais, representado árvores de conteúdos principais "Nodes" e suas conexoes que representam, o objetivo e ter uma organização didática dos conteudos.
        1. Para cada conceito, inclua seu nome, importância (como número de 1 a 5) e nível hierárquico (level).
        2. Relacione os conceitos de forma que o mapa mental seja coeso e reflita a interdependência dos elementos.
        3. O mapa mental deve seguir uma hierarquia lógica, com os conceitos mais amplos no topo e seus subconceitos de forma hierárquica abaixo.
        4. A saída deve estar no formato JSON e conter duas chaves: "nodes" e "edges".
        - "nodes" deve ser uma lista de dicionários contendo "id", "label", "importance" e "level".
        - "edges" deve ser uma lista de dicionários contendo "source" e "target".
        5. O JSON deve estar completo, válido e sem cortes ou quebras.
        6. Não inclua explicações adicionais ou texto antes ou depois do JSON.
        7. O JSON criado não deve ter indentação.
        8. Organize os conteúdos de forma que respeite o limite de 30 Nodes máximos.

        Gere um mapa mental estruturado e detalhado para o tópico "{topic}"
        """

        prompt = PromptTemplate(
            input_variables=["topic"],
            template=prompt_template,
        )

        final_prompt = prompt.format(topic=query)

        # Obter a resposta do LLM
        response = llm.invoke(final_prompt)

        # Tentar analisar a resposta como JSON
        try:
            # Extrair JSON da resposta usando expressão regular
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                json_str = match.group(0)
                data = json.loads(json_str)
                st.session_state['nodes_data'] = data["nodes"]
                st.session_state['edges_data'] = data["edges"]
                st.session_state['response'] = data

                # Armazenar a resposta no histórico
                st.session_state['response_history'].append({
                    'query': query,
                    'response': data
                })
            else:
                raise ValueError("A resposta não contém um JSON válido.")

        except Exception as e:
            st.error(f"Erro ao analisar a resposta: {e}")
            st.text("Resposta do LLM:")
            st.text(response)

# Função para exibir o gráfico
def display_graph():
    if st.session_state['nodes_data'] and st.session_state['edges_data']:
        # Definir cores e tamanhos dos nós baseados na importância e nível
        def get_node_size(importance):
            return 15 + importance * 5  # Tamanho baseado na importância

        def get_node_color(level):
            # Tons de verde para o tema dark
            colors = ['#006400', '#228B22', '#32CD32', '#7CFC00', '#ADFF2F']
            return colors[level % len(colors)]  # Seleciona cor baseado no nível hierárquico

        node_objects = [
            Node(
                id=str(node["id"]),
                label=node["label"],
                size=get_node_size(node.get("importance", 1)),
                color=get_node_color(node.get("level", 0)),
                font={'color': 'white', 'size': 12}
            )
            for node in st.session_state['nodes_data']
        ]

        edge_objects = [
            Edge(
                source=str(edge["source"]),
                target=str(edge["target"]),
            )
            for edge in st.session_state['edges_data']
        ]

        # Configuração para o agraph
        config = Config(
            width='100%',
            height=500,
            directed=True,
            physics=False,
            hierarchical=True,
        )

        # Exibir o gráfico
        return_value = agraph(nodes=node_objects, edges=edge_objects, config=config)

        # st.write(return_value)
    else:
        st.info("Por favor, insira um tema e clique em 'Mapa Mental 🗺️🧠' para gerar o mapa mental.")

# Interface do Usuário
def main():

    if not st.session_state['search_query']:
        st.header("Árvore de Conhecimento 🌳🧠")
    else:
        st.header(f"🌳 {st.session_state['search_query']} 🧠")    

    with st.sidebar:

        st.header("Pesquisa:")
        st.session_state['search_query'] = st.text_input("Tema principal 📚🔎", "")
        search_button = st.button("Mapa Mental 🗺️🧠")

        if search_button and st.session_state['search_query']:
            run_ai(st.session_state['search_query'])

        # Exibir o histórico de pesquisas como botões
        if st.session_state['response_history']:
            st.subheader("Histórico de Pesquisas")
            for i, entry in enumerate(st.session_state['response_history']):
                query_label = entry['query']
                if st.button(query_label, key=f'history_{i}'):
                    # Quando o botão é clicado, atualiza os dados dos nós e arestas
                    st.session_state['nodes_data'] = entry['response']['nodes']
                    st.session_state['edges_data'] = entry['response']['edges']
                    st.session_state['response'] = entry['response']
                    st.session_state['search_query'] = query_label

        
        st.write(f"Subscription Status: {st.session_state.user_subscribed}")
        st.write("🎉 Otimo! Você é um usuario Premium! 🎉")
        st.write(f'Usuario: {st.session_state.email}')

    # Exibir o gráfico
    with st.container(border=True):
        display_graph()

if __name__ == "__main__":
    main()
