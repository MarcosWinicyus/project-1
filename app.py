import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
import json

# Definir o layout da página como centralizado
st.set_page_config(layout="wide", 
                   page_title="Mapas Mentais 🤖", page_icon="🧠")

# Função para inicializar variáveis de estado
if 'nodes_data' not in st.session_state:
    st.session_state['nodes_data'] = None
if 'edges_data' not in st.session_state:
    st.session_state['edges_data'] = None
if 'response' not in st.session_state:
    st.session_state['response'] = None

# Estilos CSS para melhorar o design
st.markdown("""
    <style>
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border-radius: 12px;
        padding: 10px 24px;
        font-size: 16px;
    }
    .stTextInput input {
        border-radius: 12px;
        padding: 10px;
    }
    .stTextInput label {
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Título da página
st.title("Mapas Mentais 🤖🧠")

# Espaçamento para centralizar os elementos
st.header("")

SideL, SideR = st.columns((1, 1))

with st.sidebar:
    api_key = st.text_input("Insira sua OpenAI API key:", type="password")

with SideL:
    # Criar uma barra de pesquisa e um botão de pesquisa
    MarginL, col1, col2m, MarginR = st.columns((0.5, 2, 1, 0.5))
    with col1:
        search_query = st.text_input("Qual o tema principal ❓", "")
    with col2m:
        search_button = st.button("Pesquisar 🔎")

# Ação ao clicar no botão de pesquisa
if search_button:
    if not api_key:
        st.error("Por favor, insira sua OpenAI API key.")
    elif search_query:
        st.write(f"Você pesquisou por: **{search_query}**")

        # Configurar o LLM da OpenAI com a chave da API
        llm = OpenAI(openai_api_key=api_key, temperature=0, max_tokens=1500)

        # Criar um prompt template
        prompt_template = """
        Você é um especialista em criação de mapas mentais. Gere um mapa mental estruturado e detalhado para o tópico "{topic}".
        1. Para cada conceito, inclua seu nome, importância (como número de 1 a 5) e uma breve explicação sobre sua função.
        2. Relacione os conceitos de forma que o mapa mental seja coeso e reflita a interdependência dos elementos.
        3. As relações entre os conceitos devem ser claramente nomeadas, indicando o tipo de conexão (ex: "causa", "depende de", "é parte de").
        4. O mapa mental deve seguir uma hierarquia lógica, com os conceitos mais amplos no topo e seus subconceitos de forma hierárquica abaixo.
        5. A saída deve estar no formato JSON e conter duas chaves: "nodes" e "edges".
        - "nodes" deve ser uma lista de dicionários contendo "id", "label", "importance", "description" e "level" (o nível hierárquico do conceito).
        - "edges" deve ser uma lista de dicionários contendo "source", "target" e "label" (explicando a relação entre os nós).
        6. O JSON deve estar completo, válido e sem cortes ou quebras.
        7. Não inclua explicações adicionais ou texto antes ou depois do JSON.
        """

        prompt = PromptTemplate(
            input_variables=["topic"],
            template=prompt_template,
        )

        final_prompt = prompt.format(topic=search_query)

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

        except Exception as e:
            st.error(f"Erro ao analisar a resposta: {e}")
            st.text("Resposta do LLM:")
            st.text(response)

with SideR:
    # Exibir o gráfico se os dados estiverem disponíveis
    if st.session_state['nodes_data'] and st.session_state['edges_data']:
        # Definir cores e tamanhos dos nós baseados na importância e nível
        def get_node_size(importance):
            return 15 + importance * 5  # Tamanho baseado na importância

        def get_node_color(level):
            colors = ['#FFD700', '#FF8C00', '#FF4500', '#FF6347', '#8B0000']  # Cores de acordo com o nível
            return colors[level % len(colors)]  # Seleciona cor baseado no nível hierárquico

        node_objects = [
            Node(
                id=str(node["id"]),
                label=node["label"],
                size=get_node_size(node.get("importance", 1)),
                color=get_node_color(node.get("level", 0)),
                title=node["description"]
            )
            for node in st.session_state['nodes_data']
        ]

        edge_objects = [
            Edge(
                source=str(edge["source"]),
                target=str(edge["target"]),
                label=edge["label"]
            )
            for edge in st.session_state['edges_data']
        ]

        # Configuração para o agraph
        config = Config(
            width=950, height=750, directed=True, 
            physics=True, hierarchical=False,
            nodeHighlightBehavior=True, 
            maxZoom=2, minZoom=0.5,
            link={'label': 'true'}  # Exibir labels nas arestas
        )

        # Exibir o gráfico
        return_value = agraph(nodes=node_objects, edges=edge_objects, config=config)

        # Exibir a resposta JSON bruta
        with st.expander("Ver JSON gerado"):
            st.json(st.session_state['response'])
