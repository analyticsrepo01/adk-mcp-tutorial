# adk-mcp-tutorial

A comprehensive tutorial for building and testing MCP (Model Context Protocol) servers using Gemini 2.5 Pro and Google ADK.

## Overview

The Model Context Protocol (MCP) is an open standard that simplifies how AI assistants connect with external data, tools, and systems. It achieves this by standardizing the way applications provide contextual information to Large Language Models (LLMs), creating a vital interface for models to interact directly with various external services.

This tutorial demonstrates how to build custom MCP servers using Gemini 2.5 Pro with four specific examples and multiple testing approaches.

## Features

### MCP Server Code Generation
- **Example 1**: Building a BigQuery MCP Server
- **Example 2**: Building a MedlinePlus MCP Server  
- **Example 3**: Building an NIH MCP Server
- **Example 4**: Building a Cocktail MCP Server

### MCP Server Testing Options
- **Option 1**: Use LangChain MCP Adaptor (Jupyter Notebook only)
- **Option 2**: Build your own agent with Gemini
- **Option 3**: Use Google ADK

## Prerequisites

- Python 3.8+
- Google Cloud Project with Vertex AI API enabled
- Jupyter Notebook environment
- Node.js (for some MCP servers)

## Installation

Install required packages:

```bash
pip install --upgrade --quiet google-genai google-cloud-secret-manager mcp geopy black google-cloud-bigquery langchain-mcp-adapters langchain langchain-google-vertexai langgraph google-adk
```

## Getting Started

### 1. Authentication

For Google Colab users:
```python
from google.colab import auth
auth.authenticate_user()
```

### 2. Configuration

Set up your Google Cloud project:
```python
PROJECT_ID = "your-project-id"
LOCATION = "us-central1"
MODEL_ID = "gemini-2.5-flash"
```

### 3. Generated MCP Servers

The tutorial generates four MCP servers in the `server/` directory:

- `bq.py` - BigQuery integration with table listing and description tools
- `med.py` - MedlinePlus medical term lookup
- `nih.py` - NIH ICD-10 code search
- `cocktail.py` - Cocktail database with 5 different tools

## Usage Examples

### BigQuery Server
```python
query = "Please list my BigQuery tables, project id is 'my-project', location is 'us'"
```

### Medical Information
```python
query = "Please explain flu in detail"
```

### ICD-10 Codes
```python
query = "Please tell me icd-10 code for pneumonia"
```

### Cocktail Information
```python
query = "Please tell me the details of cocktail margarita"
```

## Testing Methods

### Option 1: LangChain MCP Adaptor
Best for Jupyter Notebook environments with React agent integration.

### Option 2: Custom Gemini Agent
Implements a multi-turn conversation loop with tool calling capabilities, handling:
- Tool discovery from MCP sessions
- Function call execution
- Response generation with context

### Option 3: Google ADK
Uses Google's Agent Development Kit for streamlined MCP integration with built-in session management.

## Architecture

The tutorial demonstrates MCP integration with Gemini following this flow:
1. Gemini gets tool information from MCP client session
2. User prompt sent to model with conversation history
3. Model requests tool calls with structured data
4. Tool execution results sent back to model
5. Process repeats until final response or max turns reached
6. Gemini generates final response based on tool responses

## Key Components

- **MCP Server Generation**: Automated code generation using Gemini 2.5 Pro
- **Tool Discovery**: Dynamic tool listing and schema validation
- **Multi-turn Conversations**: Context-aware conversation loops
- **Error Handling**: Robust error handling for tool execution
- **Session Management**: Proper MCP session lifecycle management

## Files Structure

```
adk-mcp-tutorial/
├── README.md
├── build_mcp_server_by_gemini.ipynb
└── server/
    ├── bq.py
    ├── med.py
    ├── nih.py
    └── cocktail.py
```

## References

- [Model Context Protocol Introduction](https://modelcontextprotocol.io/introduction)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Gemini MCP Examples](https://github.com/philschmid/gemini-samples/blob/main/examples/gemini-mcp-example.ipynb)

## License

Copyright 2025 Google LLC - Licensed under the Apache License, Version 2.0