import streamlit as st

st.set_page_config(
    page_title="MCP-Adapters Chatbot",
    page_icon="")


pages = [
    st.Page("pages/home.py", title="Welcome"),
    st.Page("pages/mcp.py", title="MCP-Adapters-Chatbot"),
    st.Page("pages/settings.py", title="Global Settings"),
    ]

pg = st.navigation(pages)
st.markdown(
    """
    <style>
    .fixed-bottom-left {
        position: fixed;
        bottom: 0;
        left: 0;
        background-color: #0f1117;
        padding: 10px;
        z-index: 999999;
        border-top-right-radius: 10px;
        box-shadow: 0px -2px 5px rgba(0, 0, 0, 0.1);
    }
    </style>
    <div class="fixed-bottom-left">
        ✉️ <a href="mailto:gibsonxue@gmail.com">Contact Us</a>
    </div>
    """,
    unsafe_allow_html=True
)
pg.run()
