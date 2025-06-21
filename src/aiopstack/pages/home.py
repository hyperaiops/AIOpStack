import streamlit as st
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

def app():
    # Custom CSS styling
    st.markdown("""
        <style>
            h3 {
                text-align: center;
                color: #4B8BBE;
            }
            .stButton>button {
                background-color: #4B8BBE;
                color: white;
                border-radius: 8px;
                height: 3em;
                font-size: 16px;
                font-weight: bold;
                width: 100%;
            }
            .stButton>button:hover {
                background-color: #306998;
                color: white;
            }
            .description-box {
                height: 160px;
                overflow: hidden;
                font-size: 14px;
                line-height: 1.4;
            }
        </style>
    """, unsafe_allow_html=True)

    # Title
    st.markdown("<h3>AIOpStack</h3>", unsafe_allow_html=True)
    st.divider()
    # 4-column layout
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("<h5>MCP-Adapters-Chatbot</h5>", unsafe_allow_html=True)
        st.image("./static/mcp.png", use_container_width=True)
        st.markdown("""
            <div class='description-box'>
                MCP Adapters Chatbot is a graphic interface built atop the
                <a href='https://github.com/langchain-ai/langchain-mcp-adapters' target='_blank'>
                langchain-mcp-adapters</a> Python library, allowing developers to visually discover and interact with MCP tools.
            </div>
        """, unsafe_allow_html=True)
        if st.button("Try Now", key="all_in_one", use_container_width=True):
            st.switch_page("pages/mcp.py")

# Run the app
app()

