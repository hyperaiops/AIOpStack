import streamlit as st
from streamlit_local_storage import LocalStorage
from streamlit_helper import _load_localstorage, _load_model
import json
import base64

localS = LocalStorage()

def update_field(field_name, encode=False):

    # Retrieve the current value of the field from Streamlit session state
    value = st.session_state.get(field_name, "")

    # Define keys for submission storage and session validation
    submitted_key = f"{field_name}_submitted"
    val_key = f"val_{field_name}"

    # If the field has a non-empty value
    if value != "":
        # Encode the value in base64 if specified (useful for sensitive data)
        if encode:
            value = base64.b64encode(value.encode("utf-8")).decode("utf-8")

        # Save the (optionally encoded) value in local storage
        localS.setItem(field_name, value, key=submitted_key)

        # Retrieve and store the saved value back into session state for validation
        st.session_state[val_key] = localS.getItem(itemKey=field_name)
    else:
        # If the value is empty, clear the corresponding session and local storage
        st.session_state[val_key] = None
        localS.deleteItem(itemKey=field_name, key=submitted_key)

def app():
    st.subheader("Global Settings")

    _load_localstorage(local_storage=localS)
    _load_model()

    with st.form("get_data"):
        st.text_input("Model Name", key="model_name", value=st.session_state["val_model_name"])
        st.text_input("API Key", key="api_key", value=st.session_state["val_api_key"], type="password")
        st.text_input("API URL", key="api_url", value=st.session_state["val_api_url"])

        # Decode mcp configuration from Base64 to string.
        val = st.session_state.get("val_mcp_config")
        mcp_config_value = base64.b64decode(val).decode("utf-8") if val else None
        json_input = st.text_area("MCP Configuration", key="mcp_config", value=mcp_config_value, height=300)

        submitted = st.form_submit_button("Submit")

        if json_input:
            try:
                # Parse and validate JSON
                parsed_json = json.loads(json_input)
                st.success("Valid JSON!")
                st.json(parsed_json)  # Display formatted JSON
            except json.JSONDecodeError:
                st.error("Invalid JSON! Please check your input.")

        if submitted:
            st.write("Successfully Submitted")
            update_field("api_key")
            update_field("api_url")
            update_field("model_name")
            update_field("mcp_config", encode=True)

app()

