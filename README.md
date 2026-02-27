# Vanna AI MCP Server

**Purpose:**  
A Model Context Protocol (MCP) server that provides a natural language interface to SQL databases using Vanna AI. It allows AI assistants (like Claude or Gemini) to generate and execute SQL queries based on plain English questions.

**Why this exists:**  
To enable seamless natural language data exploration. By bridging LLMs with your private SQL databases (via an SSH tunnel), this server allows you to "chat with your data" without manual SQL writing, all while keeping your database credentials secure on your remote server (like a DGX).

### 💰 The Free, Local Alternative
This project is designed as a **completely free, local, open-source alternative** to expensive enterprise data platforms (comparable to the AI-to-SQL features found in **Databricks** or **Snowflake**).

*   **Cost:** $0 (No per-token fees or monthly subscriptions).
*   **Privacy:** Your data stays in your infrastructure.
*   **Performance:** While it runs on anything, the results scale with your hardware. The more **GPU horsepower** (e.g., NVIDIA A100/H100 or Apple M-Series chips) you give it, the faster and more accurate your data insights become.

## Features

-   **Natural Language to SQL:** Convert user questions into executable SQL queries.
-   **SSH Tunneling:** Securely connect to remote databases (e.g., MySQL on a DGX) from any environment.
-   **Multiple LLM Providers:** Supports Ollama (local), LM Studio (local), Claude (Anthropic), Gemini (Google), and ChatGPT (OpenAI).
-   **Vector Store Training:** Uses ChromaDB to remember your database schema and common queries to improve accuracy.
-   **SSE Transport:** Built for high-performance containerized deployments using Server-Sent Events.

> [!WARNING]
> **Ollama Performance Note:** Running with local Ollama (`LLM_TYPE=ollama`) can be **slow and potentially unreliable** depending on your hardware. If you experience timeouts or inconsistent SQL generation, consider using a cloud provider like Gemini or OpenAI for production use.

## Setup

### 1. Prerequisites
-   Python 3.11+
-   A running SQL database (or SSH access to one).
-   **Local AI:** [Download Ollama](https://ollama.com/download) for local inference.

### 🍎 Mac User?
Follow the **[Mac & Local Ollama Setup Guide (50 Steps)](MAC_SETUP_GUIDE.md)** for a detailed walkthrough from zero to a running server.

### 2. Installation
```bash
git clone https://github.com/lilgreml1n/vanna-mcp
cd vanna-mcp
uv pip install -e .
```

### 3. Configuration
Create a `.env` file in the root directory:

```ini
# --- LLM CONFIG ---
LLM_TYPE=ollama  # choices: ollama, lmstudio, claude, gemini, openai

# OLLAMA CONFIG
OLLAMA_MODEL=codellama

# CLAUDE CONFIG
# ANTHROPIC_API_KEY=your_key_here
# CLAUDE_MODEL=claude-3-5-sonnet-20241022

# GEMINI CONFIG
# GEMINI_API_KEY=your_key_here
# GEMINI_MODEL=gemini-1.5-flash

# OPENAI CONFIG
# OPENAI_API_KEY=your_key_here
# OPENAI_MODEL=gpt-4o
```

## Tools Provided

-   `ask_database`: Convert a question to SQL and optionally execute it.
-   `train_vanna`: Provide DDL or example SQL to "teach" the model your schema.
-   `get_tables`: List all available tables.
-   `get_schema`: Get column details for a specific table.
-   `execute_sql`: Run manual SQL for verification.

## 🧪 Quick Start with Sample Data

If you don't have a database ready, you can set up a sample inventory database for testing:

1.  **Create Sample Database:**
    Run the included setup script in your MySQL environment:
    ```bash
    mysql -u root -p < setup_test_db.sql
    ```
    This creates an `inventory_db` with an `inventory` table and 20 sample items.

### 📋 What's in the Sample Data?
The script pre-loads diverse items so you can test immediately:
- **Nike** Air Max 90 (Men's 10.5, Black/White) in bin B-12.
- **Patagonia** Better Sweater (Unisex L) in bin A-10.
- **Adidas** Ultraboost 21 (Women's 8) in bin B-05.
- **Levi's** 501 Original Fit Jeans (32x34) in bin C-22.
- ... and 16 more realistic items across various brands!

2.  **Configure `.env`:**
    Point your `.env` to this new database:
    ```ini
    MYSQL_DATABASE=inventory_db
    # ... rest of your MySQL credentials ...
    ```

## 💻 Hardware Tested & Verified

This project has been rigorously tested across two primary environments to ensure scalability from local development to production-grade AI compute.

### 1. High-Performance AI Server (DGX-Class)
- **CPU:** 20-Core High-Performance Processor (Cortex-X925/A725 architecture)
- **RAM:** 128GB LPDDR5x
- **Storage:** 4TB NVMe Gen4 SSD
- **Usage:** Primary host for Vanna AI, MySQL databases, and large-scale vector stores. Runs multiple concurrent LLM streams (Ollama/Docker) with sub-second response times.

### 2. Local Development (MacBook Air)
- **Model:** MacBook Air (M1/M2/M3 Silicon)
- **RAM:** 16GB Unified Memory (Recommended minimum for local Ollama)
- **Usage:** Used for client-side MCP proxies and local testing of small LLM models (Llama3-8B).
- **Note:** Performance on Apple Silicon is exceptional due to integrated GPU/NPU acceleration.

## 🚀 Zero-to-AI Setup (For AI Agents)

**Our Goal:** You should be able to point any AI (Claude, Gemini, or Copilot) at this README and be running in minutes.

### 1. For Claude Desktop (Mac)
Add this to your `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "vanna-ai": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "--network=host", "-v", "vanna_chroma_data:/app/chroma_data", "--env-file", "/path/to/your/vanna-mcp/.env", "vanna-mcp-server"]
    }
  }
}
```

### 2. For Gemini CLI (Local)
In your `gemini-cli-mcp` project, update `main_mcp.py` to point to this server:
```python
MCP_SERVERS = {
    "vanna-ai": {
        "command": "docker",
        "args": ["run", "-i", "--rm", "--network=host", "vanna-mcp-server"]
    }
}
```

### 3. For GitHub Copilot / VS Code
1. Install the **MCP Extension** in VS Code.
2. Add the Vanna MCP server using the command: `docker run -i --rm --network=host vanna-mcp-server`.
3. You can now ask Copilot: `@mcp /ask_database "Show me all items in bin B-12"`

## 💡 Testing Your AI
Once connected, try these prompts:
- "How many Nike items do we have in total?"
- "What is the most expensive item we sold recently?" (Uses join on `ebay_orders`)
- "List all Adidas items that are NOT sold."

## Integration with SparkForge
This server is typically deployed on a DGX or high-performance server as part of the [SparkForge](https://github.com/lilgreml1n/sparkforge) ecosystem. It serves as the "brain" for other MCP proxies like `inventory-mcp`.
