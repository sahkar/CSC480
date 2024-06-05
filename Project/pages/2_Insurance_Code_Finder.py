import streamlit as st
import pandas as pd
from openai import OpenAI

from utils import authenticate, submit_num_results
from state import establish_openai_model, establish_openai_key

st.set_page_config(page_title='Insurance Code Finder')
st.title('Insurance Code Finder')
st.markdown('___')

if 'openai_model' not in st.session_state:
    establish_openai_model()

if 'openai_key' not in st.session_state:
    establish_openai_key()

if 'authenticated' not in st.session_state:
    authenticate()

if st.session_state.authenticated:
    with st.sidebar:
        num_results = st.number_input('Number of results', value=1, min_value=1, max_value=10, step=1, key='num_results', on_change=submit_num_results)

    if 'client' not in st.session_state:
        st.session_state.client = OpenAI(api_key=st.session_state.openai_key)

    if 'codes' not in st.session_state:
        uploaded_file = st.file_uploader('Choose a file')
        
        if uploaded_file is None:
            st.stop()
        else:
            df = pd.read_csv(uploaded_file)
            st.session_state.codes = df

    if 'messages_icf' not in st.session_state:
        st.session_state.messages_icf = [
            {"role": "system", "content":
                f'''
                You will act as an insurance agent that will compare the following insurance codes to a provided input. 
                Compare the code descriptions and the provided input and output the {num_results} most relevant results.
                Provided Insurance Codes: 
                ---
                {st.session_state.codes.to_string()}
                '''
            }
        ]

    for message in st.session_state.messages_icf:
        if message['role'] == 'system':
            split = message['content'].split('---')
            with st.chat_message(message['role']):
                st.markdown(split[0])
                st.dataframe(st.session_state.codes)
        else:
            with st.chat_message(message['role']):
                st.markdown(message['content'])


    if prompt := st.chat_input("What is up?"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages_icf.append({"role": "user", "content": prompt})

        with st.chat_message('assistant'):
            client = st.session_state.client
            stream = client.chat.completions.create(
                model=st.session_state.openai_model, 
                messages=st.session_state.messages_icf,
                stream=True,
            )
            response = st.write_stream(stream)

        st.session_state.messages_icf.append({"role": "assistant", "content": response})
