import streamlit as st
from openai import OpenAI

def establish_openai_model():
    if 'openai_model' not in st.session_state:
        st.session_state.openai_model = 'gpt-3.5-turbo' 

def establish_openai_key():
    if 'openai_key' not in st.session_state:
        with st.form('OpenAI API Key Form'):
            openai_key = st.text_input('OpenAI API Key', type='password')
            if st.form_submit_button('Submit'):
                st.session_state.openai_key = openai_key
                st.rerun()