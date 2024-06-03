import streamlit as st
from openai import OpenAI

from utils import authenticate
from state import establish_openai_model, establish_openai_key

st.set_page_config(page_title='Custom System Prompt')
st.title('Custom System Prompt')
st.markdown('___')

establish_openai_model()
establish_openai_key()

authenticate()

if 'client' not in st.session_state:
    st.session_state.client = OpenAI(api_key=st.session_state.openai_key)

with st.sidebar:
    system_prompt = st.text_area('System Prompt', placeholder='Enter a custom system prompt for your chatbot', key='system_prompt')
    st.session_state.messages_sp = [{'role': 'system', 'content': system_prompt}]

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