import os
import streamlit as st

from decouple import config

from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_groq import ChatGroq

# Configuração da API Key do GROQ
os.environ['GROQ_API_KEY'] = config('GROQ_API_KEY')

st.set_page_config(
    page_title='Assistente de Estoque',
    page_icon='📄',
)
st.header('Assistente de Estoque')

# Modelo otimizado para SQL
selected_model = 'llama3-8b-8192'

st.write('Faça perguntas sobre o estoque de produtos, preços e reposições.')

user_question = st.text_input('O que deseja saber sobre o estoque?')

# Inicializar modelo GROQ com configurações otimizadas
model = ChatGroq(
    groq_api_key=os.environ['GROQ_API_KEY'],
    model_name=selected_model,
    temperature=0.1,
    max_tokens=2048,
    timeout=60
)

# Conectar ao banco de dados
try:
    db = SQLDatabase.from_uri('sqlite:///estoque.db')
except Exception as e:
    st.error(f"❌ Erro ao conectar banco: {e}")
    st.stop()

# Configurar toolkit SQL
toolkit = SQLDatabaseToolkit(
    db=db,
    llm=model,
)

# Baixar prompt ReAct
try:
    system_message = hub.pull('hwchase17/react')
except Exception as e:
    st.error(f"❌ Erro ao carregar prompt: {e}")
    st.stop()

# Criar agente ReAct
agent = create_react_agent(
    llm=model,
    tools=toolkit.get_tools(),
    prompt=system_message,
)

# Configurar executor do agente
agent_executor = AgentExecutor(
    agent=agent,
    tools=toolkit.get_tools(),
    verbose=False,  # Removido verbose para não mostrar logs
    max_iterations=10,
    max_execution_time=120,
    handle_parsing_errors=True
)

# Template de prompt mais específico
prompt = '''
Você é um especialista em análise de estoque. Use as ferramentas SQL disponíveis para responder perguntas sobre inventário.

INSTRUÇÕES IMPORTANTES:
1. Seja direto e eficiente nas consultas SQL
2. Se uma consulta falhar, tente uma abordagem mais simples
3. Sempre formate a resposta final em português brasileiro
4. Forneça apenas a resposta final, sem explicar o processo
5. Não mencione detalhes técnicos sobre a execução da query

Pergunta do usuário: {q}

Analise a pergunta e execute as consultas necessárias para dar uma resposta completa.
'''
prompt_template = PromptTemplate.from_template(prompt)

# Interface de consulta
if st.button('Consultar'):
    if user_question:
        with st.spinner('Consultando o banco de dados...'):
            try:
                formatted_prompt = prompt_template.format(q=user_question)
                
                # Executar consulta
                try:
                    result = agent_executor.invoke({
                        'input': formatted_prompt
                    })
                    
                    # Processar e limpar a resposta
                    if 'output' in result:
                        response = result['output']
                        
                        # Remover mensagens técnicas indesejadas
                        unwanted_phrases = [
                            "Note: The query executed successfully",
                            "The results show that",
                            "executed successfully and returned",
                            "The query was executed",
                            "successfully executed"
                        ]
                        
                        for phrase in unwanted_phrases:
                            if phrase in response:
                                # Dividir por pontos e manter apenas a parte relevante
                                sentences = response.split('.')
                                cleaned_sentences = []
                                for sentence in sentences:
                                    if not any(unwanted in sentence for unwanted in unwanted_phrases):
                                        cleaned_sentences.append(sentence)
                                response = '. '.join(cleaned_sentences).strip()
                                if response and not response.endswith('.'):
                                    response += '.'
                        
                        # Exibir apenas a resposta limpa
                        if response:
                            st.markdown(response)
                        else:
                            st.warning("Não foi possível obter uma resposta clara.")
                    else:
                        st.warning("⚠️ Formato de resposta inesperado")
                
                except Exception as agent_error:
                    # Tentar consulta direta mais simples
                    try:
                        # Consulta SQL direta para casos simples
                        if "vende mais" in user_question.lower():
                            direct_query = "SELECT * FROM produtos ORDER BY vendas DESC LIMIT 5"
                        elif "estoque" in user_question.lower():
                            direct_query = "SELECT * FROM produtos WHERE quantidade > 0 LIMIT 10"
                        else:
                            direct_query = "SELECT * FROM produtos LIMIT 5"
                        
                        result = db.run(direct_query)
                        st.text(result)
                        
                    except Exception as direct_error:
                        st.error(f"❌ Erro: {direct_error}")
                
            except Exception as e:
                st.error(f"❌ Erro: {e}")
    else:
        st.warning('Por favor, insira uma pergunta.')