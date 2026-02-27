# 🍎 Mac & Local Ollama: 50-Step Ultimate Setup Guide

Follow these steps from 1 to 50 to go from a fresh Mac to a fully functional AI-powered SQL Assistant.

## 🟢 Part 1: The Foundation (Steps 1-10)

1.  **Open Terminal:** Press `Cmd + Space` and type "Terminal".
2.  **Install Homebrew:** Paste `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
3.  **Follow Homebrew Instructions:** Pay attention to the "Next steps" in your terminal to add brew to your PATH.
4.  **Install Git:** Run `brew install git`.
5.  **Install Docker Desktop:** Visit [docker.com](https://www.docker.com/products/docker-desktop/) and download the Mac version.
6.  **Open Docker Desktop:** Drag it to your Applications folder and launch it.
7.  **Accept Docker Terms:** Click through the setup wizard and wait for the green status light.
8.  **Enable VirtioFS:** In Docker settings > General, ensure "VirtioFS" is checked for best performance.
9.  **Increase Docker Resources:** In Settings > Resources, give Docker at least 8GB of RAM if possible.
10. **Install Python:** Run `brew install python@3.11`.

## 🧠 Part 2: Ollama Setup (Steps 11-20)

11. **Download Ollama:** Go to [ollama.com](https://ollama.com/download/mac).
12. **Install Ollama:** Open the `.zip`, drag the app to Applications, and launch it.
13. **Ollama in Menu Bar:** Look for the llama icon in your top menu bar.
14. **Download a Model:** In terminal, run `ollama pull llama3` (better for logic).
15. **Download a Code Model:** Run `ollama pull codellama` (better for SQL).
16. **Test Ollama:** Run `ollama run llama3 "Hello!"`. Type `/bye` to exit.
17. **Check Memory:** Ensure your Mac has at least 16GB RAM for smooth Ollama performance.
18. **Warning Note:** Local LLMs can be **slow**. On an M1/M2/M3 chip, it's fast; on Intel Macs, it will be slow.
19. **Unreliability Note:** If the SQL generated is wrong, you may need to "train" it with more DDL.
20. **Keep Ollama Running:** The Ollama app must be open in the background for this project to work.

## 📁 Part 3: Project Installation (Steps 21-30)

21. **Create Projects Folder:** Run `mkdir -p ~/projects && cd ~/projects`.
22. **Clone the Repo:** Run `git clone https://github.com/lilgreml1n/vanna-mcp`.
23. **Enter Directory:** Run `cd vanna-mcp`.
24. **Create Virtual Env:** Run `python3.11 -m venv .venv`.
25. **Activate Env:** Run `source .venv/bin/activate`.
26. **Install UV:** Run `pip install uv`.
27. **Sync Dependencies:** Run `uv pip install -e .`.
28. **Create Data Folder:** Run `mkdir -p chroma_data`.
29. **Verify Files:** Run `ls` to ensure `main.py` and `docker-compose.yml` are present.
30. **Create .env File:** Run `touch .env`.

## ⚙️ Part 4: Configuration (Steps 31-40)

31. **Open .env in Editor:** Run `open -e .env`.
32. **Set LLM Type:** Add `LLM_TYPE=ollama`.
33. **Set Ollama Model:** Add `OLLAMA_MODEL=codellama`.
34. **Configure SSH Host:** Add `SSH_HOST=192.168.x.x` (Your DGX or DB Server IP).
35. **Configure SSH User:** Add `SSH_USERNAME=your_user`.
36. **Configure SSH Pass:** Add `SSH_PASSWORD=your_password`.
37. **Set Remote MySQL Host:** Add `MYSQL_REMOTE_HOST=localhost`.
38. **Set MySQL Port:** Add `MYSQL_REMOTE_PORT=3306`.
39. **Set DB Credentials:** Add `MYSQL_USER`, `MYSQL_PASSWORD`, and `MYSQL_DATABASE`.
40. **Save .env:** Save and close the text editor.

## 🐳 Part 5: Docker & Deployment (Steps 41-50)

41. **Build Docker Image:** Run `docker compose build`.
42. **Start the Server:** Run `docker compose up -d`.
43. **Check Logs:** Run `docker logs -f vanna-mcp-server`.
44. **Look for "Ready":** Wait until logs say "Vanna AI MCP Server is ready!".
45. **Open Claude Desktop:** Ensure you have Claude Desktop installed.
46. **Open Claude Config:** Press `Cmd + Shift + G` in Finder and go to `~/Library/Application Support/Claude/`.
47. **Edit config.json:** Add the Vanna MCP server details (see main README for JSON).
48. **Restart Claude:** Fully quit and restart Claude Desktop.
49. **Ask your first question:** "Show me the first 5 rows of the inventory table."
50. **Enjoy!** You are now using local AI to query your remote database securely.

---

### ⚠️ Pro-Tips for Mac Users:
- **Intel Macs:** If Ollama is too slow, switch `.env` to `LLM_TYPE=gemini` or `openai`.
- **Permission Denied:** If Docker fails to bind ports, ensure no other service is using port 8082.
- **SSH Keys:** If you prefer SSH keys, uncomment the volumes in `docker-compose.yml`.
