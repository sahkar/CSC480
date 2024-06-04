from openai import OpenAI
import json
import streamlit as st
import pandas as pd

from tools import describe_data, selection, projection, reset_data
from state import establish_openai_key, establish_openai_model
from utils import authenticate

st.set_page_config(page_title='Dataframe Q&A')
st.title('Dataframe Q&A')
st.markdown('___')

if 'openai_model' not in st.session_state:
    establish_openai_model()

if 'openai_key' not in st.session_state:
    establish_openai_key()

if 'authenticated' not in st.session_state:
    authenticate()

if st.session_state.authenticated:
    with st.sidebar:
        generate_tool_response = st.radio('Generate model response after tool response', options=['Yes', 'No'])

    if 'client' not in st.session_state:
        st.session_state.client = OpenAI(api_key=st.session_state.openai_key)

    if 'data' not in st.session_state:
        uploaded_file = st.file_uploader('Choose a file')
        
        if uploaded_file is None:
            st.stop()
        else:
            df = pd.read_csv(uploaded_file)
            st.session_state.data = df
            st.session_state.original_data = df
            
    if 'messages_df' not in st.session_state:
        st.session_state.messages_df = []

    with st.chat_message('Data'):
        st.dataframe(st.session_state.original_data, use_container_width=True)

    for message in st.session_state.messages_df:
        if type(message) == dict:
            if message['role'] == 'tool':
                with st.chat_message(message['role']):
                    if 'data' in message['content']:
                        st.dataframe(json.loads(message['content'])['data'])
                    else:
                        st.json(message)
            else:
                with st.chat_message(message['role']):
                    st.write(message['content'])

    if prompt := st.chat_input("What is up?"):
        data:pd.DataFrame = st.session_state.data
        with st.chat_message('user'):
            st.write(prompt)
        messages_df = st.session_state.messages_df
        messages_df.append({"role": "user", "content": prompt})
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "describe_data",
                    "description": "Describe the dataset",
                    "parameters": {
                        "type": "object",
                        "properties": {
                        },
                        "required": [],
                    },
                },
            }, 
            {
                "type": "function",
                "function": {
                    "name": "selection",
                    "description": 
                        f'''
                        Convert the provided natural language prompt into an algebraic prompt using Python relational operators ex: ('A > B & B == C' where A, B, C are column names). 
                        Query the dataset using python relational operators prompt. 
                        Equivalent to relational algebra selection. 
                        Modifies the dataset.
                        ''',
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": f"Python algebraic string using relational operators that will be used to query the dataset. Must conform to the following schema {data.columns}",
                            },
                        },
                        "required": ["prompt"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "projection",
                    "description": 
                        f'''
                        Convert the provided natural language prompt into a list of column names that must be selected from the dataset. 
                        Equivalent to relational algebra projection. 
                        Modifies the dataset.
                        ''',
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "columns": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "description": f"A column from the data. Must conform to the following schema {data.columns}"
                                }
                            },
                        },
                        "required": ["columns"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "reset_data",
                    "description": 
                        f'''
                        Undos any modifications to the dataset. 
                        Resets the dataset to the original data. 
                        Can be called upon requests. 
                        ''',
                    "parameters": {
                        "type": "object",
                        "properties": {
                        },
                        "required":['']
                    },
                },
            },
        ]

        response = st.session_state.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages_df,
            tools=tools,
            tool_choice="auto", 
        )
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        if tool_calls:
            available_functions = {
                "describe_data": describe_data, 
                "selection": selection,
                "projection": projection,
                "reset_data": reset_data
            } 
            messages_df.append(response_message)
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)

                if function_name in ('describe_data', 'reset_data'):
                    function_response = function_to_call()
                
                elif function_name == 'selection':
                    st.write(function_args)
                    function_response = function_to_call(prompt = function_args.get("prompt"))
                
                elif function_name == 'projection':
                    st.write(function_args)
                    function_response = function_to_call(columns = function_args.get("columns"))
                
                with st.chat_message('tool'):
                    try:
                        st.dataframe(json.loads(function_response)['data'])
                    except:
                        st.json(function_response)

                messages_df.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )
            
            if generate_tool_response == 'Yes':
                stream = st.session_state.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages_df,
                    stream=True
                ) 

                with st.chat_message('assistant'):
                    response_content = st.write_stream(stream)
            else:
                response_content = ''
            messages_df.append({'role': 'assistant', 'content': response_content})

        else:
            response_content = response_message.content

            messages_df.append({'role': 'assistant', 'content': response_content})
            with st.chat_message('assistant'):
                st.write(response_content)
            
        st.session_state.messages_df = messages_df

