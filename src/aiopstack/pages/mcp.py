import asyncio
import time
import uuid
import sys
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.types import Command
from graphs.mcp.nodes import build_graph
from streamlit_helper import _load_model, _load_localstorage
import logging
from streamlit_local_storage import LocalStorage

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

localS = LocalStorage()

# MCP call status
FuncCallState = {
    'default': 'default',  # Initial status
    'discarded': 'discarded',  # MCP call is rejected and human feedback is required.
    'interrupted': 'interrupted',  # human feedback is required.
    'approved': 'approved'  # MCP call is approved.
}


async def invoke_our_graph(st_messages, st_placeholder):
    container = st_placeholder  # This container will hold the dynamic Streamlit UI components
    thoughts_placeholder = container.container()  # Container for displaying status messages
    token_placeholder = container.empty()  # Placeholder for displaying progressive token updates
    final_text = ""  # Will store the accumulated text from the model's response
    async for event in st.session_state.mcp_graph['graph_instance'].astream_events(
            input=st_messages,
            config={"configurable": {"thread_id": st.session_state.mcp_graph['thread_id']}},
            version="v2"):
        try:
            kind = event["event"]  # Determine the type of event received

            if kind == "on_chat_model_stream":
                # The event corresponding to a stream of new content (tokens or chunks of text)
                addition = event["data"]["chunk"].content  # Extract the new content chunk
                final_text += addition  # Append the new content to
                # the accumulated text
                if addition:
                    token_placeholder.write(final_text)  # Update the st placeholder with the progressive response

            elif kind == "on_chain_stream" and not isinstance(event["data"]["chunk"], Command):
                chunk_data = event["data"]["chunk"]

                if "__interrupt__" in event["data"]["chunk"]:
                    st.session_state.mcp_graph['mcp_approve'] = FuncCallState['interrupted']
                    with thoughts_placeholder:
                        status_placeholder = st.empty()  # Placeholder to show the tool's status
                        with status_placeholder.status("Human FeedBack Required", expanded=True) as s:
                            interrupt_data = chunk_data['__interrupt__'][0].value
                            tool_calls = interrupt_data.get('tool_call', [])
                            for i, tool in enumerate(tool_calls):
                                st.write(f"Step {i}: ", tool['name'])
                                st.code(tool['args'])  # Display the input data sent to the tool
                            st.write("Action Need: ")
                            st.code(interrupt_data.get('question'))

                            col1, col2 = st.columns(2)
                            with col1:
                                st.button("✅ Agree", on_click=agree_action)
                            with col2:
                                st.button("❌ Cancel", on_click=discard_action)

            elif kind == "on_tool_start":
                # The event signals that a tool is about to be called
                with thoughts_placeholder:
                    status_placeholder = st.empty()  # Placeholder to show the tool's status
                    with status_placeholder.status("Thinking...", expanded=False) as s:
                        time.sleep(1.5)
                        st.write("Called ", event['name'])  # Show which tool is being called
                        st.write("Tool input: ")
                        st.code(event['data'].get('input'))  # Display the input data sent to the tool
                        st.write("Tool output: ")
                        output_placeholder = st.empty()  # Placeholder for tool output that will be updated later below
                        s.update(label=f"Completed Calling Tool!", expanded=True)  # Update the status once done

            elif kind == "on_tool_end":
                # The event signals the completion of a tool's execution
                with thoughts_placeholder:
                    # We assume that `on_tool_end` comes after `on_tool_start`, meaning output_placeholder exists
                    if 'output_placeholder' in locals():
                        output_placeholder.code(event['data'].get('output').content)  # Display the tool's output

        except KeyError as e:
            st.error(f"⚠️ Missing expected data field: {e}")
            continue
        except Exception as e:
            st.error(f"⛔ Error processing event: {str(e)}")
            continue
    # Return the final aggregated message after all events have been processed
    return final_text

def reset_session():
    del st.session_state["mcp_graph"]
    st.rerun()

def app():
    _load_localstorage(localS)
    _load_model()

    st.markdown("## MCP Adapters Chatbot")
    if st.button("🔄 New Chat"):
        reset_session()
    st.divider()

    # Sidebar with instructions and suggestions
    st.sidebar.markdown("""

    """)
    # Session initialization
    if "mcp_graph" not in st.session_state:
        st.session_state.mcp_graph = {}
        st.session_state.mcp_graph['thread_id'] = uuid.uuid4()
        st.session_state.mcp_graph['graph_instance'] = (
            asyncio.run(
                build_graph(llm=st.session_state['base_model'],
                            config=st.session_state["val_mcp_config"])
            )
        )

    if "messages" not in st.session_state.mcp_graph:
        st.session_state.mcp_graph['messages'] = [
            AIMessage(content="Hi, I am your MCP Assistant. How may I help you...")
        ]

    if "mcp_approve" not in st.session_state.mcp_graph:
        st.session_state.mcp_graph['mcp_approve'] = FuncCallState['default']

    # Display existing chat history
    for msg in st.session_state.mcp_graph['messages']:
        role = "assistant" if isinstance(msg, AIMessage) else "user"
        st.chat_message(role).write(msg.content)

    # Handle user input
    if prompt := st.chat_input():
        st.session_state.mcp_graph['messages'].append(HumanMessage(content=prompt))
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            placeholder = st.container()

            if st.session_state.mcp_graph['mcp_approve'] in [FuncCallState['discarded'], FuncCallState['interrupted']]:
                # User discarded the previous suggestion, handle feedback
                response = asyncio.run(invoke_our_graph(
                    Command(resume={"action": "feedback", "data": prompt}),
                    placeholder
                ))
                if response:
                    st.session_state.mcp_graph['mcp_approve'] = FuncCallState['default']
            else:
                # Regular AI interaction
                response = asyncio.run(invoke_our_graph(
                    {"messages": st.session_state.mcp_graph['messages'][-1]},
                    placeholder
                ))

            st.session_state.mcp_graph['messages'].append(AIMessage(response))

    # Handle approved action
    if st.session_state.mcp_graph['mcp_approve'] == FuncCallState['approved']:
        st.write('✅ Action is approved!')

        with st.chat_message("assistant"):
            placeholder = st.container()
            response = asyncio.run(invoke_our_graph(
                Command(resume={"action": "continue"}),
                placeholder
            ))
            st.session_state.mcp_graph['messages'].append(AIMessage(response))

        st.session_state.mcp_graph['mcp_approve'] = FuncCallState['default']

    # Handle discarded action
    elif st.session_state.mcp_graph['mcp_approve'] == FuncCallState['discarded']:
        st.write('⛔ Action is discarded! Please give your feedback.')


# Approval State Setter Functions
def agree_action():
    """Handle approved action state."""
    st.session_state.mcp_graph['mcp_approve'] = 'approved'


def discard_action():
    """Handle discarded action state."""
    st.session_state.mcp_graph['mcp_approve'] = FuncCallState['discarded']


# auth_utils.ensure_azure_login(app)
app()
