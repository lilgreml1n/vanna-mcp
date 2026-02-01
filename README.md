# Vanna AI MCP Server

MCP (Model Context Protocol) server that enables AI assistants to query databases using natural language via Vanna AI.

## Features

- 🗣️ **Natural Language SQL**: Ask questions in plain English, get SQL queries automatically
- 🔐 **Secure SSH Tunneling**: Connects to remote databases via SSH with key or password auth
- 🤖 **AI Training**: Train Vanna on your database schema and sample queries
- 🔌 **MCP Compatible**: Works with Claude Desktop, Gemini CLI, and other MCP clients
- 📊 **ChromaDB Vector Store**: Persistent storage for trained SQL patterns

## Quick Start

### Using Docker (Recommended)

```bash
# Create .env file (see .env.sample)
cp .env.sample .env
# Edit .env with your credentials

# Run with Docker Compose
docker-compose up -d
```

Server runs on **http://localhost:8000**

### Local Installation

```bash
# Install with uv
uv pip install vanna chromadb sshtunnel python-dotenv mcp starlette uvicorn

# Run the server
uv run python main.py
```

## Configuration

Create a `.env` file with these variables:

```bash
# SSH Tunnel Configuration
SSH_HOST=your-server.com
SSH_PORT=22
SSH_USERNAME=your-user
SSH_PASSWORD=your-password          # OR use key-based auth
SSH_KEY_PATH=/path/to/private/key   # Optional
SSH_KEY_PASSPHRASE=key-passphrase   # Optional

# MySQL Database (on remote server)
MYSQL_REMOTE_HOST=localhost  # Usually localhost when using tunnel
MYSQL_REMOTE_PORT=3306
MYSQL_DATABASE=your_database
MYSQL_USER=db_user
MYSQL_PASSWORD=db_password

# Vanna AI
VANNA_MODEL=chinook            # Your model name
VANNA_API_KEY=your-api-key     # Get from vanna.ai
```

## Available MCP Tools

- `generate_sql` - Generate SQL from natural language question
- `run_sql` - Execute SQL query and return results
- `train_question_sql` - Train Vanna with example question/SQL pairs
- `train_ddl` - Train Vanna on database schema (DDL statements)
- `get_training_data` - View all trained examples

## Usage Examples

### With Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "vanna-ai": {
      "command": "uv",
      "args": ["run", "python", "/absolute/path/to/fastmcp/main.py"]
    }
  }
}
```

### Example Queries

```
You: Show me the top 5 customers by total sales
Claude: [generates and runs SQL query]

You: What tables are in the database?
Claude: [calls get_training_data to see schema]

You: Train this: "show active users" -> SELECT * FROM users WHERE active=1
Claude: [calls train_question_sql]
```

## Project Structure

```
fastmcp/
├── main.py              # MCP server with Vanna integration
├── docker-compose.yml   # Docker deployment
├── Dockerfile
├── pyproject.toml       # uv dependencies
├── .env.sample          # Configuration template
└── chroma_data/         # ChromaDB vector storage (persistent)
```

## Tech Stack

- **Vanna AI**: Natural language to SQL conversion
- **ChromaDB**: Vector database for training data storage
- **MCP**: Model Context Protocol for AI tool integration
- **SSH Tunnel**: Secure remote database access
- **FastAPI/Starlette**: HTTP server framework

## Security Notes

- Never commit `.env` file to version control
- Use SSH key authentication when possible
- Database credentials are transmitted only through SSH tunnel
- ChromaDB data is persisted in `chroma_data/` directory

## License

Personal use. Database access and credentials remain private.
