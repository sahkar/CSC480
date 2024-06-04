import json
import pandas as pd
import streamlit as st

# def get_columns(): 
#     """Get the columns of the dataset"""
#     data:pd.DataFrame = st.session_state.data
#     return json.dumps({'columns': list(data.columns)})


def describe_data():
    """Describes the dataset"""
    data:pd.DataFrame = st.session_state.data
    return json.dumps({'data': data.describe().to_dict()})

def selection(prompt:str):
    """Query the dataset using a python relational algebra prompt. Equivalent to relational algebra projection. """
    data:pd.DataFrame = st.session_state.data
    df = data.query(prompt)
    st.session_state.data = df
    return json.dumps({'data': df.to_dict()})

def projection(columns:list):
    """Select columns from the dataset. Equivalent to relational algebra selection"""
    data:pd.DataFrame = st.session_state.data
    df = data.loc[:, columns]
    st.session_state.data = df
    return json.dumps({'data': df.to_dict()})

def reset_data():
    st.session_state.data = st.session_state.original_data
    data:pd.DataFrame = st.session_state.data
    return json.dumps({'data': data.to_dict()})