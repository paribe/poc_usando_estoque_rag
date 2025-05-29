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
    page_title='Estoque GPT - GROQ',
    page_icon='⚡',
)
st.header('Assistente de Estoque - GROQ')

# Modelos disponíveis no GROQ (muito mais rápidos!)
groq_models = [
    'llama3-8b-8192',      # Llama 3 8B - Rápido e eficiente
    'llama3-70b-8192',     # Llama 3 70B - Mais potente
    'mixtral-8x7b-32768',  # Mixtral - Ótimo para tarefas complexas
    'gemma-7b-it',         # Gemma 7B - Google
]

# Modelo padrão recomendado para análise de dados
selected_model = 'llama3-8b-8192'

st.sidebar.markdown('### ⚡ Powered by GROQ')
st.sidebar.markdown('**Velocidade ultra-rápida de inferência!**')
st.sidebar.markdown(f'**Modelo ativo:** {selected_model}')
st.sidebar.markdown('**Provider:** GROQ Lightning Fast AI')

st.write('Faça perguntas sobre o estoque de produtos, preços e reposições.')
st.info('🚀 Agora com velocidade GROQ - respostas em segundos!')

user_question = st.text_input('O que deseja saber sobre o estoque?')

# Inicializar modelo GROQ
model = ChatGroq(
    groq_api_key=os.environ['GROQ_API_KEY'],
    model_name=selected_model,
    temperature=0,  # Para respostas mais consistentes em análise de dados
    max_tokens=1024
)

# Conectar ao banco de dados
try:
    db = SQLDatabase.from_uri('sqlite:///estoque.db')
    st.sidebar.success("✅ Banco conectado")
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
    verbose=True,
    max_iterations=5,  # Limitar iterações para velocidade
    handle_parsing_errors=True
)

# Template de prompt otimizado para GROQ
prompt = '''
Utilize os recursos disponíveis para atender consultas sobre o inventário da empresa. 
Você deve oferecer análises detalhadas sobre mercadorias, valores, necessidades de 
reabastecimento e documentos solicitados pelos usuários.
Apresente suas respostas de forma clara e organizada para facilitar a compreensão.
Comunique-se exclusivamente em idioma português do Brasil.

IMPORTANTE: Seja direto e objetivo nas consultas SQL. Use GROQ's speed advantage!

Pergunta: {q}
'''
prompt_template = PromptTemplate.from_template(prompt)

# Interface de consulta
if st.button('⚡ Consultar com GROQ'):
    if user_question:
        with st.spinner('🚀 Consultando com velocidade GROQ...'):
            try:
                formatted_prompt = prompt_template.format(q=user_question)
                
                # Medir tempo de resposta
                import time
                start_time = time.time()
                
                output = agent_executor.invoke({'input': formatted_prompt})
                
                end_time = time.time()
                response_time = end_time - start_time
                
                # Exibir resultado
                st.markdown(output.get('output'))
                
                # Mostrar estatísticas de performance
                st.sidebar.markdown('### 📊 Performance')
                st.sidebar.metric("Tempo de resposta", f"{response_time:.2f}s")
                st.sidebar.markdown(f"**Modelo:** {selected_model}")
                
            except Exception as e:
                st.error(f"❌ Erro durante consulta: {e}")
                st.info("💡 Verifique se a GROQ_API_KEY está configurada corretamente")
    else:
        st.warning('Por favor, insira uma pergunta.')

# Informações adicionais sobre GROQ
with st.expander("ℹ️ Sobre GROQ vs OpenAI"):
    st.markdown("""
    **🚀 Vantagens do GROQ:**
    - ⚡ **Velocidade**: 10-100x mais rápido que OpenAI
    - 💰 **Custo**: Significativamente mais barato
    - 🔓 **Open Source**: Modelos Llama, Mixtral, Gemma
    - 🎯 **Especializado**: Hardware otimizado para inferência
    
    **🎯 Ideal para:**
    - Aplicações que precisam de resposta rápida
    - Prototipagem e desenvolvimento
    - Aplicações com muitas consultas
    - Análise de dados em tempo real
    """)

# Nota sobre configuração
st.markdown("---")
st.caption("💡 Configure sua GROQ_API_KEY no arquivo .env para usar este assistente")