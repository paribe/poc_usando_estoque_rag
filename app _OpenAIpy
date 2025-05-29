import os
import streamlit as st

from decouple import config

from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI


os.environ['OPENAI_API_KEY'] = config('OPENAI_API_KEY')

st.set_page_config(
    page_title='Estoque GPT',
    page_icon='📄',
)
st.header('Assistente de Estoque')

# Modelo fixo automático - GPT-4o-mini (equilibrio entre performance e custo)
selected_model = 'gpt-4o-mini'

st.write('Faça perguntas sobre o estoque de produtos, preços e reposições.')
user_question = st.text_input('O que deseja saber sobre o estoque?')

model = ChatOpenAI(
    model=selected_model,
)

db = SQLDatabase.from_uri('sqlite:///estoque.db')
toolkit = SQLDatabaseToolkit(
    db=db,
    llm=model,
)
system_message = hub.pull('hwchase17/react')

agent = create_react_agent(
    llm=model,
    tools=toolkit.get_tools(),
    prompt=system_message,
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=toolkit.get_tools(),
    verbose=True,
)

prompt = '''
Utilize os recursos disponíveis para atender consultas sobre o inventário da empresa. 
Você deve oferecer análises detalhadas sobre mercadorias, valores, necessidades de 
reabastecimento e documentos solicitados pelos usuários.
Apresente suas respostas de forma clara e organizada para facilitar a compreensão.
Comunique-se exclusivamente em idioma português do Brasil.
Pergunta: {q}
'''
prompt_template = PromptTemplate.from_template(prompt)

if st.button('Consultar'):
    if user_question:
        with st.spinner('Consultando o banco de dados...'):
            formatted_prompt = prompt_template.format(q=user_question)
            output = agent_executor.invoke({'input': formatted_prompt})
            st.markdown(output.get('output'))
    else:
        st.warning('Por favor, insira uma pergunta.')