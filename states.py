import streamlit as st

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
    if 'wiki_content' not in st.session_state:
        st.session_state['wiki_content'] = None
    if 'user_subscribed' not in st.session_state:
        st.session_state['user_subscribed'] = False
        
