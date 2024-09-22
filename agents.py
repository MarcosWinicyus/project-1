import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import json
import re

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# Função para ajustar a query do usuário
def adjust_query(query):
    api_key = st.secrets["openai_api_key"]
    if not api_key:
        st.error("API key não encontrada. Por favor, verifique seu arquivo secrets.toml.")
        return query
    else:
        # Configurar o LLM da OpenAI com a chave da API
        llm = ChatOpenAI(openai_api_key=api_key,
                         temperature=0,
                         max_tokens=100,
                         model='gpt-4')

        # Criar um prompt template para ajustar a query
        system_prompt = """
        Você é um assistente de pesquisas que revisa a consulta do usuário para que seja adequada para uma pesquisa na Wikipedia.
        Caso necessario faça correções ortograficas para a lingua portuguesa. 
        Caso necessario ajuste a pesquisa para ser objetiva que possa ser pesquisada na Wikipedia.
        Forneça apenas o tema ajustado, sem explicações adicionais.
        """

        prompt_template = "{system_prompt}\n\nConsulta do usuário: \"{query}\""

        prompt = PromptTemplate(input_variables=["system_prompt", "query"], template=prompt_template)
        final_prompt = prompt.format(system_prompt=system_prompt, query=query)

        # Obter a resposta do LLM
        response = llm.invoke(final_prompt)

        # Retornar a resposta ajustada
        return response.content.strip()

# Função para executar o LLM e gerar o mapa mental
def run_ai(query, context=''):
    api_key = st.secrets["openai_api_key"]
    if not api_key:
        st.error("API key não encontrada. Por favor, verifique seu arquivo secrets.toml.")
    else:
        # Configurar o LLM da OpenAI com a chave da API
        llm = ChatOpenAI(openai_api_key=api_key,
                         temperature=0,
                        #  max_tokens=3000,
                         model='gpt-4')

        # Criar um prompt template
        prompt_template = """
        Você é um especialista em criação de mapas mentais, representando árvores de conteúdos principais "Nodes" e suas conexões. O objetivo é ter uma organização didática dos conteúdos.

        Use as seguintes informações como contexto para criar o mapa mental:

        {context}

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

        prompt = PromptTemplate(input_variables=["topic", "context"], template=prompt_template)
        final_prompt = prompt.format(topic=query, context=context)

        # Obter a resposta do LLM
        response = llm.invoke(final_prompt)

        # Tentar analisar a resposta como JSON
        try:
            # Extrair JSON da resposta usando expressão regular
            match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if match:
                json_str = match.group(0)
                data = json.loads(json_str)
                st.session_state['nodes_data'] = data["nodes"]
                st.session_state['edges_data'] = data["edges"]
                st.session_state['response'] = data

                # Armazenar a resposta no histórico
                st.session_state['response_history'].append({
                    'query': query,
                    'response': data,
                    'wiki_content': context
                })
            else:
                raise ValueError("A resposta não contém um JSON válido.")

        except Exception as e:
            st.error(f"Erro ao analisar a resposta: {e}")
            st.text("Resposta do LLM:")
            st.text(response.content)

# Função para buscar conteúdo na Wikipedia
def search_wikipedia(query):
    wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(lang="pt", top_k_results=3, doc_content_chars_max=10000, load_all_available_meta=True))

    search_result = wikipedia.run(query)
    
    return search_result

# Função principal que orquestra as chamadas
def run_agent():
    user_query = st.session_state['search_query']

    # Ajustar a query do usuário usando o LLM
    adjusted_query = adjust_query(user_query)

    # Armazenar a query ajustada no estado da sessão
    st.session_state['adjusted_query'] = adjusted_query

    # Buscar conteúdo na Wikipedia com a query ajustada
    wiki_content = search_wikipedia(adjusted_query)

    # Armazenar o conteúdo da Wikipedia no estado da sessão
    st.session_state['wiki_content'] = wiki_content

    # Concatenar o conteúdo da Wikipedia com a consulta original do usuário
    combined_context = wiki_content

    # Gerar o mapa mental usando o LLM com o contexto combinado
    run_ai(user_query, context=combined_context)
