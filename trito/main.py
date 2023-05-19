#!/usr/bin/env python3

import yaml
from yaml.loader import SafeLoader

import streamlit as st
import streamlit_chat as sc

from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate, LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)

def reset_session():
    st.session_state['messages'] = [
        SystemMessage(content='''
Você é um consultor de moda com o objetivo de auxiliar o vendedor em uma loja de roupas e acessórios.
Você deve interagir com o vendedor e não com o cliente.
Sugira peças de roupas e acessórios para o cliente que combinem bem e que sejam confortáveis.
Leve em consideração a idade aproximada do cliente, gênero com o qual se identifica, e o propósito da roupa.
Comece fazendo perguntas ao vendedor para conhecer o cliente e o propósito da vestimenta.
A cada interação, sugira peças de roupa adequadas e peça a opinião do cliente, ajuste as próximas sugestões baseadas nessas opiniões e na disponibilidade da peça de roupa na loja.
    '''),
        HumanMessage(content='Olá! Eu sou seu vendedor. Vamos começar um atendimento?'),
    ]

@st.cache_resource
def chatbot():
    return ChatOpenAI(
        model_name='gpt-3.5-turbo',
        temperature=0.2,
        openai_api_key=st.secrets['openai_api_key']
    )

chat = chatbot()

def main():
    st.title('Seu consultor de moda')
    messages_placeholder = st.empty()

    if 'messages' not in st.session_state:
        reset_session()

    with st.form(key='my_form', clear_on_submit=True):
        response = st.text_input('Você:', key='user_input')
        submitted = st.form_submit_button(label='Enviar')

    if submitted:
        if response == '/reset':
            reset_session()
        elif response:
            st.session_state['messages'].append(HumanMessage(content=response))

    if 'messages' in st.session_state:
        with messages_placeholder.container():
            for idx, message in enumerate(st.session_state['messages']):
                if isinstance(message, AIMessage):
                    sc.message(f'Assistente: {message.content}', key=f'bot_{idx}')
                elif isinstance(message, HumanMessage):
                    sc.message(f'Você: {message.content}', is_user=True, key=f'human_{idx}')

            if isinstance(st.session_state['messages'][-1], HumanMessage):
                next_message = chat(st.session_state['messages'])
                st.session_state['messages'].append(next_message)
                sc.message(f'Assistente: {next_message.content}', key=f'bot__')

def check_password():
    def password_entered():
        '''Checks whether a password entered by the user is correct.'''
        if st.session_state['password'] == st.secrets['password']:
            st.session_state['password_correct'] = True
            del st.session_state['password']  # don't store password
        else:
            st.session_state['password_correct'] = False

    if 'password_correct' not in st.session_state:
        # First run, show input for password.
        st.text_input(
            'Password', type='password', on_change=password_entered, key='password'
        )
        return False
    elif not st.session_state['password_correct']:
        # Password not correct, show input + error.
        st.text_input(
            'Password', type='password', on_change=password_entered, key='password'
        )
        st.error('😕 Password incorrect')
        return False
    else:
        # Password correct.
        return True

if check_password():
    main()
