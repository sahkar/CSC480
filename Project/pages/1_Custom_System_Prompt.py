import streamlit as st
from openai import OpenAI

from utils import authenticate, submit_system_prompt
from state import establish_openai_model, establish_openai_key

st.set_page_config(page_title='Custom System Prompt')
st.title('Custom System Prompt')
st.markdown('___')

if 'openai_model' not in st.session_state:
    establish_openai_model()

if 'openai_key' not in st.session_state:
    establish_openai_key()

if 'authenticated' not in st.session_state:
    authenticate()

if st.session_state.authenticated:
    if 'client' not in st.session_state:
        st.session_state.client = OpenAI(api_key=st.session_state.openai_key)

    with st.sidebar:
        system_prompt = st.text_area('System Prompt', placeholder='Enter a custom system prompt for your chatbot', key='system_prompt', on_change=submit_system_prompt)

    if 'messages_sp' not in st.session_state:
        st.session_state.messages_sp = [{'role': 'system', 'content': system_prompt}]

    for message in st.session_state.messages_sp:
        with st.chat_message(message['role']):
            st.markdown(message['content'])


    if prompt := st.chat_input("What is up?"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages_sp.append({"role": "user", "content": prompt})

        with st.chat_message('assistant'):
            client = st.session_state.client
            stream = client.chat.completions.create(
                model=st.session_state.openai_model, 
                messages=st.session_state.messages_sp,
                stream=True,
            )
            response = st.write_stream(stream)

        st.session_state.messages_sp.append({"role": "assistant", "content": response})