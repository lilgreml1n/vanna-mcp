# Vanna AI MCP Server

**Purpose:**  
A Model Context Protocol (MCP) server that provides a natural language interface to SQL databases using Vanna AI. It allows AI assistants (like Claude or Gemini) to generate and execute SQL queries based on plain English questions.

**Why this exists:**  
To enable seamless natural language data exploration. By bridging LLMs with your private SQL databases (via an SSH tunnel), this server allows you to "chat with your data" without manual SQL writing, all while keeping your database credentials secure on your remote server (like a DGX).

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
-   (Optional) Ollama or LM Studio for local inference.

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
    This creates an `inventory_db` with an `inventory` table and 10 sample items.

2.  **Configure `.env`:**
    Point your `.env` to this new database:
    ```ini
    MYSQL_DATABASE=inventory_db
    # ... rest of your MySQL credentials ...
    ```

3.  **Test Queries:**
    Once the server is running, try asking:
    *   "How many Nike items do we have?"
    *   "What is the total sale price of all sold items?"
    *   "List all items in bin B-12."

## Integration with SparkForge
This server is typically deployed on a DGX or high-performance server as part of the [SparkForge](https://github.com/lilgreml1n/sparkforge) ecosystem. It serves as the "brain" for other MCP proxies like `inventory-mcp`.
