#!/usr/bin/env python3
"""
Vanna AI MCP Server with SSH Tunnel Support
Allows Claude to query databases using natural language via Vanna AI
Credentials loaded from .env file
"""

import asyncio
import os
from pathlib import Path
from typing import Any
import vanna as vn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from sshtunnel import SSHTunnelForwarder
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.routing import Route
import uvicorn
import signal
import sys
import logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Global instances
vanna_instance = None
ssh_tunnel = None

def get_ssh_config():
    """Load SSH configuration from environment variables"""
    config = {
        'ssh_host': os.getenv('SSH_HOST'),
        'ssh_port': int(os.getenv('SSH_PORT', 22)),
        'ssh_username': os.getenv('SSH_USERNAME'),
        'ssh_password': os.getenv('SSH_PASSWORD'),
        'ssh_pkey': os.getenv('SSH_KEY_PATH'),
        'ssh_private_key_password': os.getenv('SSH_KEY_PASSPHRASE'),
        'remote_mysql_host': os.getenv('MYSQL_REMOTE_HOST', 'localhost'),
        'remote_mysql_port': int(os.getenv('MYSQL_REMOTE_PORT', 3306)),
    }
    
    if not config['ssh_host'] or not config['ssh_username']:
        raise ValueError("SSH_HOST and SSH_USERNAME are required in .env file")
    
    if not config['ssh_password'] and not config['ssh_pkey']:
        raise ValueError("Either SSH_PASSWORD or SSH_KEY_PATH must be set in .env file")
    
    return config

def get_mysql_config():
    """Load MySQL configuration from environment variables"""
    config = {
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'database': os.getenv('MYSQL_DATABASE'),
    }
    
    if not all(config.values()):
        raise ValueError("MYSQL_USER, MYSQL_PASSWORD, and MYSQL_DATABASE are required in .env file")
    
    return config

def init_vanna():
    """Initialize Vanna with SSH tunnel to remote MySQL"""
    global ssh_tunnel, vanna_instance
    
    logging.info("Loading configuration from .env file...")
    ssh_config = get_ssh_config()
    mysql_config = get_mysql_config()
    
    logging.info(f"Establishing SSH tunnel to {ssh_config['ssh_host']}:{ssh_config['ssh_port']}...")
    
    tunnel_kwargs = {
        'ssh_address_or_host': (ssh_config['ssh_host'], ssh_config['ssh_port']),
        'ssh_username': ssh_config['ssh_username'],
        'remote_bind_address': (ssh_config['remote_mysql_host'], ssh_config['remote_mysql_port']),
    }
    
    if ssh_config['ssh_pkey']:
        tunnel_kwargs['ssh_pkey'] = ssh_config['ssh_pkey']
        if ssh_config['ssh_private_key_password']:
            tunnel_kwargs['ssh_private_key_password'] = ssh_config['ssh_private_key_password']
        logging.info(f"Using SSH key authentication: {ssh_config['ssh_pkey']}")
    else:
        tunnel_kwargs['ssh_password'] = ssh_config['ssh_password']
        logging.info("Using SSH password authentication")
    
    ssh_tunnel = SSHTunnelForwarder(**tunnel_kwargs)
    ssh_tunnel.start()
    
    logging.info(f"SSH tunnel established on local port {ssh_tunnel.local_bind_port}")
    
    llm_type = os.getenv('LLM_TYPE', 'ollama')
    vanna_model = os.getenv('VANNA_MODEL', 'my-vanna-model')
    logging.info(f"Initializing Vanna with {llm_type}...")
    
    if llm_type == "ollama":
        from vanna.ollama import Ollama
        from vanna.chromadb import ChromaDB_VectorStore
        
        class MyVanna(ChromaDB_VectorStore, Ollama):
            def __init__(self, config=None):
                ChromaDB_VectorStore.__init__(self, config=config)
                Ollama.__init__(self, config=config)
        
        model = os.getenv('OLLAMA_MODEL', 'codellama')
        vn_instance = MyVanna(config={'model': model})
        logging.info(f"Using Ollama model: {model} with ChromaDB vector store")
    
    elif llm_type == "lmstudio":
        from vanna.openai import OpenAI_Chat
        from vanna.chromadb import ChromaDB_VectorStore
        
        class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
            def __init__(self, config=None):
                ChromaDB_VectorStore.__init__(self, config=config)
                OpenAI_Chat.__init__(self, config=config)
        
        vn_instance = MyVanna(config={
            'api_key': 'not-needed',
            'base_url': 'http://localhost:1234/v1',
            'model': 'local-model'
        })
        logging.info("Using LM Studio with ChromaDB vector store")
    
    elif llm_type == "claude":
        from vanna.anthropic import Anthropic_Chat
        from vanna.chromadb import ChromaDB_VectorStore
        
        class MyVanna(ChromaDB_VectorStore, Anthropic_Chat):
            def __init__(self, config=None):
                ChromaDB_VectorStore.__init__(self, config=config)
                Anthropic_Chat.__init__(self, config=config)
        
        model = os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY required in .env for Claude")
        vn_instance = MyVanna(config={'api_key': api_key, 'model': model})
        logging.info(f"Using Claude model: {model} with ChromaDB vector store")
    
    else:
        raise ValueError(f"Unknown LLM_TYPE: {llm_type}")
    
    logging.info(f"Connecting to MySQL database '{mysql_config['database']}\...")
    
    import pymysql
    
    def run_sql_function(sql: str):
        connection = pymysql.connect(
            host='127.0.0.1',
            port=ssh_tunnel.local_bind_port,
            user=mysql_config['user'],
            password=mysql_config['password'],
            database=mysql_config['database'],
            cursorclass=pymysql.cursors.DictCursor
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                if sql.strip().upper().startswith('SELECT') or sql.strip().upper().startswith('SHOW') or sql.strip().upper().startswith('DESCRIBE'):
                    results = cursor.fetchall()
                    import pandas as pd
                    return pd.DataFrame(results)
                else:
                    connection.commit()
                    return f"Query executed successfully. Rows affected: {cursor.rowcount}"
        finally:
            connection.close()
    
    vn_instance.run_sql = run_sql_function
    vn_instance.run_sql_is_set = True
   
    df = vn_instance.run_sql("SELECT COUNT(*) as count FROM inventory")
    logging.info(f"{df}") 
    logging.info(f"Connected to MySQL database: {mysql_config['database']}")
    logging.info("=" * 60)
    logging.info("Vanna AI MCP Server is ready!")
    logging.info("=" * 60)
    
    return vn_instance

def cleanup():
    global ssh_tunnel
    print("\nShutting down...")
    if ssh_tunnel:
        ssh_tunnel.stop()
        print("SSH tunnel closed")
    print("Goodbye!")

def signal_handler(sig, frame):
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

app = Server("vanna-ai-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="ask_database",
            description="Ask a natural language question about the database. Vanna AI will convert it to SQL and execute it.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Natural language question about the data"
                    },
                    "auto_execute": {
                        "type": "boolean",
                        "description": "Whether to automatically execute the generated SQL",
                        "default": True
                    }
                },
                "required": ["question"]
            }
        ),
        Tool(
            name="train_vanna",
            description="Train Vanna AI with DDL, documentation, or example queries to improve accuracy",
            inputSchema={
                "type": "object",
                "properties": {
                    "training_type": {
                        "type": "string",
                        "enum": ["ddl", "documentation", "question_sql"],
                        "description": "Type of training data"
                    },
                    "ddl": {
                        "type": "string",
                        "description": "DDL statement (CREATE TABLE, etc.)"
                    },
                    "documentation": {
                        "type": "string",
                        "description": "Documentation about tables or columns"
                    },
                    "question": {
                        "type": "string",
                        "description": "Example question"
                    },
                    "sql": {
                        "type": "string",
                        "description": "Corresponding SQL query"
                    }
                },
                "required": ["training_type"]
            }
        ),
        Tool(
            name="get_tables",
            description="Get a list of all tables in the database",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_schema",
            description="Get the schema/structure of a specific table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table to get schema for"
                    }
                },
                "required": ["table_name"]
            }
        ),
        Tool(
            name="execute_sql",
            description="Directly execute a SQL query (use with caution - read-only recommended)",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "SQL query to execute"
                    }
                },
                "required": ["sql"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    global vanna_instance
    
    if vanna_instance is None:
        return [TextContent(
            type="text",
            text="Error: Vanna not initialized. Please check your .env configuration."
        )]
    
    try:
        if name == "ask_database":
            question = arguments.get("question")
            auto_execute = arguments.get("auto_execute", True)
            
            sql = vanna_instance.generate_sql(question)
            
            result_text = f"Question: {question}\n\nGenerated SQL:\n```sql\n{sql}\n```\n\n"
            
            if auto_execute:
                df = vanna_instance.run_sql(sql)
                result_text += f"Results:\n{df.to_string()}\n\n"
                result_text += f"Total rows: {len(df)}"
            else:
                result_text += "SQL generated but not executed (auto_execute=False)"
            
            return [TextContent(type="text", text=result_text)]
        
        elif name == "train_vanna":
            training_type = arguments.get("training_type")
            
            if training_type == "ddl":
                ddl = arguments.get("ddl")
                vanna_instance.train(ddl=ddl)
                return [TextContent(type="text", text=f"Successfully trained on DDL")]
            
            elif training_type == "documentation":
                doc = arguments.get("documentation")
                vanna_instance.train(documentation=doc)
                return [TextContent(type="text", text=f"Successfully trained on documentation")]
            
            elif training_type == "question_sql":
                question = arguments.get("question")
                sql = arguments.get("sql")
                vanna_instance.train(question=question, sql=sql)
                return [TextContent(type="text", text=f"Successfully trained on question-SQL pair")]
        
        elif name == "get_tables":
            df = vanna_instance.run_sql("SHOW TABLES")
            return [TextContent(type="text", text=f"Tables in database:\n{df.to_string()}")]
        
        elif name == "get_schema":
            table_name = arguments.get("table_name")
            df = vanna_instance.run_sql(f"DESCRIBE {table_name}")
            return [TextContent(type="text", text=f"Schema for table '{table_name}':\n{df.to_string()}")]
        
        elif name == "execute_sql":
            sql = arguments.get("sql")
            df = vanna_instance.run_sql(sql)
            return [TextContent(
                type="text",
                text=f"Query executed successfully.\n\nResults:\n{df.to_string()}\n\nTotal rows: {len(df)}"
            )]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Main entry point - using SSE transport for Docker"""
    global vanna_instance
    
    try:
        vanna_instance = init_vanna()
        
        sse = SseServerTransport("/messages")
        
        async def handle_sse(request):
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await app.run(
                    streams[0], streams[1],
                    app.create_initialization_options()
                )
        
        async def handle_messages(request):
            await sse.handle_post_message(request.scope, request.receive, request._send)
        
        starlette_app = Starlette(
            routes=[
                Route("/sse", endpoint=handle_sse),
                Route("/messages", endpoint=handle_messages, methods=["POST"]),
            ]
        )
        
        logging.info("Starting SSE server on port 8080...")
        config = uvicorn.Config(starlette_app, host="0.0.0.0", port=8082, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
        
    except Exception as e:
        print(f"Error during initialization: {e}")
        cleanup()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
