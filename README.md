# 📚 Academic MCP

[English](README.md) | [中文](README_zh.md)

🔬 `academic-mcp` is a Python-based MCP server that enables users to search, download, and read academic papers from various platforms. It provides three main tools:
- 🔎 **`paper_search`**: Search papers across multiple academic databases
- 📥 **`paper_download`**: Download paper PDFs, return paths of downloaded files
- 📖 **`paper_read`**: Extract and read text content from papers

![PyPI](https://img.shields.io/pypi/v/academic-mcp.svg) ![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Python](https://img.shields.io/badge/python-3.10+-blue.svg)

---

## 📑 Table of Contents

- [🎬 Screenshot](#-screenshot)
- [📝 TODO](#-todo)
- [✨ Features](#-features)
- [📦 Installation](#-installation)
  - [⚡ Quick Start](#-quick-start)
  - [🛠️ For Development](#️-for-development)
- [🚀 Usage](#-usage)
  - [🔎 Search Papers](#1-search-papers-paper_search)
  - [📥 Download Papers](#2-download-papers-paper_download)
  - [📖 Read Papers](#3-read-papers-paper_read)
  - [⚙️ Environment Variables](#️-environment-variables)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## ✨ Features

- 🌐 **Multi-Source Support**: Search and download papers from arXiv, PubMed, bioRxiv, medRxiv, Google Scholar, IACR ePrint Archive, Semantic Scholar, and CrossRef.
- 🎯 **Unified Interface**: All platforms accessible through consistent `paper_search`, `paper_download`, and `paper_read` tools.
- 📊 **Standardized Output**: Papers are returned in a consistent dictionary format via the `Paper` class.
- ⚡ **Asynchronous Operations**: Efficiently handles concurrent searches and downloads using `httpx` and async/await.
- 🔌 **MCP Integration**: Compatible with MCP clients for LLM context enhancement.
- 🧩 **Extensible Design**: Easily add new academic platforms by extending the `sources` module.

## 🎬 Screenshot

<img src="assets/screenshot.png" alt="Screenshot" width="800">

## 📝 TODO

Planned Academic Platforms

- [x] arXiv
- [x] PubMed
- [x] bioRxiv
- [x] medRxiv
- [x] Google Scholar
- [x] IACR ePrint Archive
- [x] Semantic Scholar
- [x] CrossRef
- [ ] PubMed Central (PMC)
- [ ] Science Direct
- [ ] Springer Link
- [ ] IEEE Xplore
- [ ] ACM Digital Library
- [ ] Web of Science
- [ ] Scopus
- [ ] JSTOR
- [ ] ResearchGate
- [ ] CORE
- [ ] Microsoft Academic

## 📦 Installation

`academic-mcp` can be installed using `uv` or `pip`. Below are detailed installation guides for different scenarios.

### ⚡ Quick Install

Install the package:

```bash
pip install academic-mcp
```

Or using uv (recommended for faster installation):

```bash
uv pip install academic-mcp
```

### 🔧 MCP Client Configuration

Choose your MCP client and follow the configuration steps:

<details>
<summary><b>1️⃣ Claude Desktop</b></summary>

**Location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Configuration:**
```json
{
  "mcpServers": {
    "academic-mcp": {
      "command": "python",
      "args": ["-m", "academic_mcp"],
      "env": {
        "SEMANTIC_SCHOLAR_API_KEY": "",
        "ACADEMIC_MCP_DOWNLOAD_PATH": "./downloads"
      }
    }
  }
}
```

**Using with uvx (alternative):**
```json
{
  "mcpServers": {
    "academic-mcp": {
      "command": "uvx",
      "args": ["academic-mcp"],
      "env": {
        "SEMANTIC_SCHOLAR_API_KEY": "",
        "ACADEMIC_MCP_DOWNLOAD_PATH": "./downloads"
      }
    }
  }
}
```

</details>

<details>
<summary><b>2️⃣ Claude Code (CLI)</b></summary>

**Location:** `~/.config/claude/config.json`

**Configuration:**
```json
{
  "mcpServers": {
    "academic-mcp": {
      "command": "python",
      "args": ["-m", "academic_mcp"],
      "env": {
        "SEMANTIC_SCHOLAR_API_KEY": "",
        "ACADEMIC_MCP_DOWNLOAD_PATH": "./downloads"
      }
    }
  }
}
```

**Verify Installation:**
```bash
# Check if academic-mcp is loaded
claude mcp list

# Test the server
claude mcp test academic-mcp
```

</details>

<details>
<summary><b>3️⃣ Cline (VS Code Extension)</b></summary>

**Location:** VS Code Settings → Extensions → Cline → MCP Settings

**Method 1: Through VS Code Settings UI**
1. Open VS Code Settings (Cmd/Ctrl + ,)
2. Search for "Cline MCP"
3. Click "Edit in settings.json"
4. Add the configuration:

```json
{
  "cline.mcpServers": {
    "academic-mcp": {
      "command": "python",
      "args": ["-m", "academic_mcp"],
      "env": {
        "SEMANTIC_SCHOLAR_API_KEY": "",
        "ACADEMIC_MCP_DOWNLOAD_PATH": "./downloads"
      }
    }
  }
}
```

**Method 2: Direct settings.json Edit**

Edit `~/.config/Code/User/settings.json` (Linux/macOS) or `%APPDATA%\Code\User\settings.json` (Windows):

```json
{
  "cline.mcpServers": {
    "academic-mcp": {
      "command": "python",
      "args": ["-m", "academic_mcp"],
      "env": {
        "SEMANTIC_SCHOLAR_API_KEY": "",
        "ACADEMIC_MCP_DOWNLOAD_PATH": "./downloads"
      }
    }
  }
}
```

</details>

<details>
<summary><b>4️⃣ Zed Editor</b></summary>

**Location:** `~/.config/zed/settings.json`

**Configuration:**
```json
{
  "context_servers": {
    "academic-mcp": {
      "command": {
        "path": "python",
        "args": ["-m", "academic_mcp"]
      },
      "settings": {
        "env": {
          "SEMANTIC_SCHOLAR_API_KEY": "",
          "ACADEMIC_MCP_DOWNLOAD_PATH": "./downloads"
        }
      }
    }
  }
}
```

</details>

<details>
<summary><b>5️⃣ Custom MCP Client</b></summary>

For other MCP clients, use the standard MCP server configuration:

**Server Command:**
```bash
python -m academic_mcp
```

**Environment Variables:**
- `SEMANTIC_SCHOLAR_API_KEY`: Optional API key for Semantic Scholar
- `ACADEMIC_MCP_DOWNLOAD_PATH`: Download directory (default: `./downloads`)

**Server Capabilities:**
- Tools: `paper_search`, `paper_download`, `paper_read`
- Transport: stdio
- Protocol: MCP 1.0

</details>

### 📝 Configuration Notes

> **API Keys:**
> - `SEMANTIC_SCHOLAR_API_KEY` is optional and only enhances Semantic Scholar features
> - All other sources work without API keys
>
> **Download Path:**
> - Use absolute paths for `ACADEMIC_MCP_DOWNLOAD_PATH` to avoid confusion
> - Ensure the directory exists or the server will create it
> - Example: `/Users/yourusername/Documents/papers` or `C:\Users\yourusername\papers`
>
> **Python Environment:**
> - Ensure `python` command points to Python 3.10+
> - For virtual environments, use the full path: `/path/to/venv/bin/python`
> - For conda: `/path/to/conda/envs/yourenv/bin/python`

### 🛠️ For Development

For developers who want to modify the code or contribute:

1. **Setup Environment**:

   ```bash
   # Install uv if not installed
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Clone repository
   git clone https://github.com/LinXueyuanStdio/academic-mcp.git
   cd academic-mcp

   # Create and activate virtual environment
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install Dependencies**:

   ```bash
   # Install dependencies (recommended)
   uv pip install -e .

   # Add development dependencies (optional)
   uv pip install pytest flake8
   ```

---

## 🚀 Usage

Once configured, `academic-mcp` provides three main tools accessible through Claude Desktop or any MCP-compatible client:

### 1. Search Papers (`paper_search`)

Search for academic papers across multiple sources:

```python
# Search arXiv for machine learning papers
paper_search([
    {"searcher": "arxiv", "query": "machine learning", "max_results": 5}
])

# Search multiple platforms simultaneously
paper_search([
    {"searcher": "arxiv", "query": "deep learning", "max_results": 5},
    {"searcher": "pubmed", "query": "cancer immunotherapy", "max_results": 3},
    {"searcher": "semantic", "query": "climate change", "max_results": 4, "year": "2020-2023"}
])

# Search all platforms (omit "searcher" parameter)
paper_search([
    {"query": "quantum computing", "max_results": 10}
])
```

### 2. Download Papers (`paper_download`)

Download paper PDFs using their identifiers:

```python
paper_download([
    {"searcher": "arxiv", "paper_id": "2106.12345"},
    {"searcher": "pubmed", "paper_id": "32790614"},
    {"searcher": "biorxiv", "paper_id": "10.1101/2020.01.01.123456"},
    {"searcher": "semantic", "paper_id": "DOI:10.18653/v1/N18-3011"}
])
```

### 3. Read Papers (`paper_read`)

Extract and read text content from papers:

```python
# Read an arXiv paper
paper_read(searcher="arxiv", paper_id="2106.12345")

# Read a PubMed paper
paper_read(searcher="pubmed", paper_id="32790614")

# Read a Semantic Scholar paper
paper_read(searcher="semantic", paper_id="DOI:10.18653/v1/N18-3011")
```

### Environment Variables

- `SEMANTIC_SCHOLAR_API_KEY`: Optional API key for enhanced Semantic Scholar features
- `ACADEMIC_MCP_DOWNLOAD_PATH`: Directory for downloaded PDFs (default: `./downloads`)

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the Repository**:
   Click "Fork" on GitHub.

2. **Clone and Set Up**:

   ```bash
   git clone https://github.com/yourusername/academic-mcp.git
   cd academic-mcp
   uv pip install -e .  # Install in development mode
   ```

3. **Make Changes**:

   - Add new platforms in `academic_mcp/sources/`.
   - Update tests in `tests/`.

4. **Submit a Pull Request**:
   Push changes and create a PR on GitHub.

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

---

Happy researching with `academic-mcp`! If you encounter issues, open a GitHub issue.
