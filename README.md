# AIOpStack

[![Python ≥3.8](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)](https://www.python.org/)
[![LangChain v0.3.25](https://img.shields.io/badge/LangChain-0.3.25-blue.svg)](https://pypi.org/project/langchain/)
[![LangGraph v0.4.8](https://img.shields.io/badge/LangGraph-0.4.8-orange.svg)](https://pypi.org/project/langgraph/)
[![LangChain MCP Adapters v0.1.7](https://img.shields.io/badge/LangChain--MCP--Adapters-0.1.7-purple.svg)](https://pypi.org/project/langchain-mcp-adapters/)

---
**Build your AIOps MCP Agent within 5 minutes.**

AIOpStack is a collection of AI Operational Agents built with Langchain/LangGraph and Streamlit‑based GUI for operational interaction and visualization.

🌐 [English](README.md) | [简体中文](README.zh.md)

### 🎯 Motivation

1. **Fast‑boot** – AIOpStack drastically reduces study and setup time for DevOps, Sysadmins and Developers.   
2. **Lightweight** – IDEs like Cursor and VSCode with Cline are resource‑heavy. AIOpStack stays minimal and nimble.  
3. **Local Deployment** – Deploy locally to access private environments.  
4. **Free & Open** – Fully open‑source, no vendor lock‑in or licensing fees.

### 🚀 Features

- **OpenAI‑compatible LLM API Integration** – Connect to any OpenAI‑compatible LLM endpoint.  
- **MCP Integration** – Seamless bridge between LLMs and popular MCP tools (e.g., Kubernetes, Ansible).  
- **Human‑in‑the‑loop Feedback** – Pause for confirmation or iterative refinement at key steps.  
- **Pure Python & GUI‑free** – Fully Python‑powered: no frontend skills required for reuse or extension.

**Video Demo**

![Demo Video](media/demo_en.gif)

### Agents Repository
| Agent Name                     | Description                                                                                                                                                  | Reference Link                                                                                          |
|--------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| langchain-mcp-adapters-chatbot | A chatbot application that leverages `langchain-mcp-adapters`, fully inheriting the configuration from the official Langchain project. Useful for testing MCP servers. | [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters/blob/main/README.md)    |



### 📖 Quick Start

#### Requirements

- Python 3.8+  
- OpenAI‑compatible LLM API URL & Key

#### Installation

```bash
pip install aiopstack
```

#### Usage Examples
run `aiops` with no parameter
```bash
aiops
```
the project can be listening at 0.0.0.0:8051 by default.

#### ⚙️ MCP Settings

> **Note:**
> 
> The settings must be written in JSON format.
> - For `stdio` mode:
>   - The `args` parameter must use an **absolute path**.
>   - Windows uses `\\` for paths, Linux uses `/`.
>   - Ensure all required **Python dependencies are pre-installed**.
> - For `sse` and `streamable_http` modes:
>   - It is recommended to use a **fully qualified domain name (FQDN)** or a valid **IP address** to avoid connectivity issues.

##### MCP Configuration Example 
The following configurations correspond to test examples located in the [`test_mcp_servers/`](./test_mcp_servers/) directory.
```json
{
  "math": {
    "command": "python",
    "args": ["C:\\Users\\yfxue\\PycharmProjects\\aiopstack\\test_mcp_server\\math_server.py"],
    "transport": "stdio"
  },
  "weather": {
    "url": "http://192.168.2.103:8000/sse/",
    "transport": "sse"
  }
}
```
**Strongly recommended**: follow up the official document [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters/blob/main/README.md)

## 🤝 Contributing

We welcome contributions! If you have suggestions or feature requests, feel free to open an issue or submit a pull request.

### Development Setup

1. Clone the repository:

```bash
git clone https://github.com/ohtaman/streamlit-desktop-app.git
```

2. Install dependencies:

```bash
cd src/aiopstack
pip install -r requirements.txt
```

3. Run Streamlit
```bash
streamlit run app.py
```


