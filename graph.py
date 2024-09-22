import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config


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
            directed=False,
            physics=True,
            hierarchical=True,
        )

        # Exibir o gráfico
        return_value = agraph(nodes=node_objects, edges=edge_objects, config=config)

        st.write(return_value)
    # else:
        # st.info("Por favor, insira um tema e clique em 'Mapa Mental 🗺️🧠' para gerar o mapa mental.")
