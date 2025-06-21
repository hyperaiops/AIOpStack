import os

import streamlit as st
from streamlit_local_storage import LocalStorage
from langchain_openai import ChatOpenAI


def _load_model():
    if 'base_model' not in st.session_state:
        st.session_state['base_model'] = None

    print('Loading base model...')

    # Define required session state variables
    required_vars = ['val_api_url', 'val_api_key', 'val_model_name']

    # Check for missing variables
    missing_vars = [var for var in required_vars if not st.session_state.get(var)]

    if missing_vars:
        # Display error with missing variables
        st.error(f"Missing required session state variables: {', '.join(missing_vars)}. \n\n"
                 f"Please fill in these variables with value in the Global Settings")
        return  # Exit early if variables are missing

    try:
        # Initialize OpenAI model
        st.session_state['base_model'] = ChatOpenAI(
            openai_api_base=st.session_state['val_api_url'],
            openai_api_key=st.session_state['val_api_key'],
            model=st.session_state['val_model_name'],
            temperature=0,
            max_tokens=None,
            timeout=30,
            max_retries=2,
        )
        print("Model loaded successfully")

    except Exception as e:
        st.error(f"Error loading model: {str(e)}")


def _load_localstorage(local_storage):
    """
    Retrieves 'api_key' and 'api_url' from the browser's local storage
    and stores them in Streamlit's session state with keys 'val_api_key' and 'val_api_url'.
    Also initializes 'val_model_name' in session state with a default value.
    """
    # local_storage = LocalStorage()
    keys = ["api_key", "api_url", "model_name", "mcp_config"]

    for key in keys:
        value = local_storage.getItem(itemKey=key)
        session_key = f"val_{key}"
        if value:
            st.session_state[session_key] = value
        elif os.getenv(key.upper()):
            st.session_state[session_key] = os.getenv(key.upper())
        else:
            st.session_state[session_key] = None