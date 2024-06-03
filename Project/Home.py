from openai import OpenAI, AuthenticationError
import streamlit as st

from utils import authenticate
from state import establish_openai_model, establish_openai_key

st.title('Home')
st.markdown('---')

establish_openai_model()
establish_openai_key()

authenticate()

st.subheader('Welcome to out CSC 480 AI Final Project!')
"""
Experiment with \n
1. Custom System Prompt
2. An Insurance Code Finder: An example of a custom system prompt
3. A Pandas Powered ChatBot: An example of function calling and tools
"""

st.markdown('---')
st.subheader('Learn more about function calling')
st.video('https://www.youtube.com/watch?v=i-oHvHejdsc')


