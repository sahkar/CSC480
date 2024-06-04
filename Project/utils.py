import streamlit as st
from openai import OpenAI, AuthenticationError

def validate_openai_key(openai_key):
    try:
        client = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model=st.session_state.openai_model, 
            messages=[{'role': 'user', 'content': 'test'}],
        )
        return True
    except AuthenticationError:
        return False

def authenticate():
    if 'openai_model' in st.session_state and 'openai_key' in st.session_state:
        if validate_openai_key(st.session_state.openai_key):
            st.toast('Valid OpenAI Key')
            st.session_state.authenticated = True
        else:
            st.error('Invalid OpenAI Key')
            del st.session_state.openai_key
    else:
        st.stop()

def submit_num_results():
    st.session_state.messages_icf = [
        {"role": "system", "content":
            f'''
            You will act as an insurance agent that will compare the following insurance codes to a provided input. 
            Compare the code descriptions and the provided input and output the {st.session_state.num_results} most relevant results.
            Provided Insurance Codes: 
            ---
            {st.session_state.codes.to_string()}
            '''
        }
    ]

def submit_system_prompt():
    st.session_state.messages_sp = [{'role': 'system', 'content': st.session_state.system_prompt}]
