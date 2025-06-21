from typing import *
import json
import base64
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai.chat_models.base import BaseChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode
from langgraph.types import Command, interrupt

def human_review_node(state) -> Command[Literal["call_llm", "tools"]]:

    print('--Human Review Node--')
    # print('--last_message--',state["messages"][-1])

    last_message = state["messages"][-1]
    tool_call = last_message.tool_calls

    # this is the value we'll be providing via Command(resume=<human_review>)
    human_review = interrupt(
        {
            "question": "Do you agree to execute?",
            # Surface tool calls for review
            "tool_call": tool_call,
        }
    )

    review_action = human_review["action"]
    review_data = human_review.get("data")

    # if approved, call the tool
    if review_action == "continue":
        return Command(goto="tools")

    # provide feedback to LLM
    elif review_action == "feedback":
        # NOTE: we're adding feedback message as a ToolMessage
        # to preserve the correct order in the message history
        # (AI messages with tool calls need to be followed by tool call messages)
        tool_messages = []

        for tool in tool_call:
            tool_message = {
                "role": "tool",
                # This is our natural language feedback
                "content": review_data,
                "name": tool["name"],
                "tool_call_id": tool["id"],
            }
            tool_messages.append(tool_message)
        return Command(goto="call_llm", update={"messages": tool_messages })

def route_after_llm(state) -> Literal[END, "human_review_node"]:
    if len(state["messages"][-1].tool_calls) == 0:
        return END
    else:
        return "human_review_node"

async def build_graph(llm: BaseChatOpenAI, config) -> CompiledStateGraph:


    mcp_dict = json.loads(base64.b64decode(config).decode("utf-8"))

    client = MultiServerMCPClient(mcp_dict)

    tools = await client.get_tools()
    def call_llm(state: MessagesState) -> MessagesState:
        response = llm.bind_tools(tools).invoke(state["messages"])
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node(call_llm)
    builder.add_node(human_review_node)
    builder.add_node(ToolNode(tools))

    builder.add_edge(START, "call_llm")
    builder.add_conditional_edges("call_llm", route_after_llm)
    builder.add_edge("tools", "call_llm")

    memory = MemorySaver()

    graph = builder.compile(checkpointer=memory)

    return graph