import streamlit as st
from st_paywall import add_auth
from streamlit_agraph import agraph, Node, Edge, Config
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
import json

# Definir o layout da página como centralizado
st.set_page_config(layout="wide", 
                   page_title="3Knowledge 🌳🧠", page_icon="🌳🧠")

add_auth(required=True,
        login_button_text="Login with Google",
        login_button_color="#FD504D",
        login_sidebar=False)

# ONLY AFTER THE AUTHENTICATION + SUBSCRIPTION, THE USER WILL SEE THIS ⤵
# The email and subscription status is stored in session state.
st.write(f"Subscription Status: {st.session_state.user_subscribed}")
st.write("🎉 Yay! You're all set and subscribed! 🎉")
st.write(f'By the way, your email is: {st.session_state.email}')


# Função para inicializar variáveis de estado
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

def run_ai():
    if not api_key and st.session_state['search_query'] != None:
        st.error("Por favor, insira sua OpenAI API key.")
    else:
        # Configurar o LLM da OpenAI com a chave da API
        llm = OpenAI(openai_api_key=api_key,
                    temperature=0,
                    max_tokens=3000)

        # Criar um prompt template
        prompt_template = """
        Você é um especialista em criação de mapas mentais, representado árvores de conteúdos principais "Nodes" e suas conexoes que representam, o objetivo e ter uma organização didática dos conteudos .
        1. Para cada conceito, inclua seu nome, importância (como número de 1 a 5)
        2. Relacione os conceitos de forma que o mapa mental seja coeso e reflita a interdependência dos elementos.
        3. O mapa mental deve seguir uma hierarquia lógica, com os conceitos mais amplos no topo e seus subconceitos de forma hierárquica abaixo.
        4. A saída deve estar no formato JSON e conter duas chaves: "nodes" e "edges".
        - "nodes" deve ser uma lista de dicionários contendo "id", "label", "importance",e "level" (o nível hierárquico do conceito).
        - "edges" deve ser uma lista de dicionários contendo "source" e "target".
        5. O JSON deve estar completo, válido e sem cortes ou quebras.
        6. Não inclua explicações adicionais ou texto antes ou depois do JSON.
        7. O JSON criado não deve ter indentação.
        8. Organize os conteúdos de forma que respeite o limite de 30 Nodes maximos.
        
        Gere um mapa mental estruturado e detalhado para o tópico "{topic}"
        """

        prompt = PromptTemplate(
            input_variables=["topic"],
            template=prompt_template,
        )

        final_prompt = prompt.format(topic=st.session_state['search_query'])

        # Obter a resposta do LLM
        response = llm.invoke(final_prompt)

        # Tentar analisar a resposta como JSON
        try:
            # Remover espaços em branco e caracteres extras
            response = response.strip()
            # Verificar se a resposta começa e termina com chaves
            if not response.startswith('{') or not response.endswith('}'):
                raise ValueError("A resposta não é um JSON válido.")

            data = json.loads(response)
            st.session_state['nodes_data'] = data["nodes"]
            st.session_state['edges_data'] = data["edges"]
            st.session_state['response'] = response

            # Armazenar a resposta no histórico
            st.session_state['response_history'].append(response)

        except Exception as e:
            st.error(f"Erro ao analisar a resposta: {e}")
            st.text("Resposta do LLM:")
            st.text(response)

st.title("Árvore de Conhecimento🌳🧠")

with st.sidebar:

    # st.logo("🌳🧠")
    st.session_state['search_query'] = st.text_input("Tema de estudo 📚🔎", "")
    # Criar uma barra de pesquisa e um botão de pesquisa
    col1, col2 = st.columns((2, 1.2))
    
    
    # with col2m:
    with col1:
        search_button = st.button("Mapa Mental 🗺️🧠", on_click=run_ai)
    
    with col2:
        Estudar = st.button("3K 🌳📚", disabled=True)

    # Exibir o histórico de respostas
    if st.session_state['response_history']:
        st.subheader("Histórico de Respostas")
        for i, resp in enumerate(st.session_state['response_history']):
            with st.expander(f"Resposta {i+1}"):
                st.json(resp)

    api_key = st.text_input("Insira sua OpenAI API key:", type="password")


# Exibir o gráfico se os dados estiverem disponíveis
with st.container(border=True):
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
                # size=get_node_size(node.get("importance", 1)),
                color=get_node_color(node.get("level", 0)),
                font={'color': 'white', 'size': 12} 
                # title=node["description"]
            )
            for node in st.session_state['nodes_data']
        ]

        edge_objects = [
            Edge(
                source=str(edge["source"]),
                target=str(edge["target"]),
                # label=edge["label"]
            )
            for edge in st.session_state['edges_data']
        ]

        # Configuração para o agrap
        config = Config(
            width='720vh',
            height=500,
            directed=True, 
            physics=False,
            hierarchical=True,
            # levelSeparation=250,
            # nodeSpacing=200,
            # treeSpacing=200,
            # blockShifting=True
        )

        # Exibir o gráfico
        return_value = agraph(nodes=node_objects, edges=edge_objects, config=config)

        st.write(return_value)

# Exibir a resposta JSON bruta
with st.expander("Ver JSON gerado"):
    if st.session_state['nodes_data'] and st.session_state['edges_data']:
        st.json(st.session_state['response'])


