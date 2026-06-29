# 📚 Academic MCP

[English](README.md) | [中文](README_zh.md)

🔬 `academic-mcp` 是一个基于 Python 的 MCP 服务器，使用户能够从各种平台搜索、下载和阅读学术论文。它提供三个主要工具：
- 🔎 **`paper_search`**：跨多个学术数据库搜索论文
- 📥 **`paper_download`**：下载论文 PDF，返回下载文件的路径
- 📖 **`paper_read`**：提取和阅读论文的文本内容

![PyPI](https://img.shields.io/pypi/v/academic-mcp.svg) ![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Python](https://img.shields.io/badge/python-3.10+-blue.svg)

---

## 📑 目录

- [🎬 演示](#-演示)
- [📝 待办事项](#-待办事项)
- [✨ 特性](#-特性)
- [📦 安装](#-安装)
  - [⚡ 快速开始](#-快速开始)
  - [🛠️ 开发环境](#️-开发环境)
- [🚀 使用](#-使用)
  - [🔎 搜索论文](#1-搜索论文-paper_search)
  - [📥 下载论文](#2-下载论文-paper_download)
  - [📖 阅读论文](#3-阅读论文-paper_read)
  - [⚙️ 环境变量](#️-环境变量)
- [🤝 贡献](#-贡献)
- [📄 许可证](#-许可证)

---

## ✨ 特性

- 🌐 **多源支持**：从 19+ 学术数据库搜索和下载论文，包括 arXiv、PubMed、PubMed Central、bioRxiv、medRxiv、Google Scholar、IACR ePrint Archive、Semantic Scholar、CrossRef、Science Direct、Springer、IEEE Xplore、Scopus、CORE 等。
- 🎯 **统一接口**：通过一致的 `paper_search`、`paper_download` 和 `paper_read` 工具访问所有平台。
- 📊 **标准化输出**：通过 `Paper` 类以一致的字典格式返回论文。
- ⚡ **异步操作**：使用 `httpx` 和 async/await 高效处理并发搜索和下载。
- 🔌 **MCP 集成**：与 MCP 客户端兼容，用于增强 LLM 上下文。
- 🧩 **可扩展设计**：通过扩展 `sources` 模块轻松添加新的学术平台。

## 🎬 演示

<img src="assets/screenshot_zh.png" alt="演示截图" width="800">

## 📝 支持的学术平台

### ✅ 已完全实现（19个数据源）

**免费开放访问：**
- [x] **arXiv** - 物理、数学、计算机科学等领域的预印本库
- [x] **PubMed** - 生物医学文献数据库
- [x] **PubMed Central (PMC)** - 免费全文生物医学和生命科学文章
- [x] **bioRxiv** - 生物学预印本服务器
- [x] **medRxiv** - 健康科学预印本服务器
- [x] **Semantic Scholar** - AI驱动的研究工具
- [x] **CrossRef** - DOI注册机构和元数据提供商
- [x] **Google Scholar** - 学术搜索引擎
- [x] **IACR ePrint Archive** - 密码学预印本
- [x] **CORE** - 开放获取研究论文聚合器

**需要API密钥：**
- [x] **Science Direct** - Elsevier的全文科学数据库（需要Elsevier API密钥）
- [x] **Springer Link** - Springer的科学出版物（需要Springer API密钥）
- [x] **IEEE Xplore** - IEEE的数字图书馆（需要IEEE API密钥）
- [x] **Scopus** - Elsevier的摘要和引文数据库（需要Scopus API密钥）

**需要机构访问：**
- [x] **ACM Digital Library** - ACM的计算文献（无公共API）
- [x] **Web of Science** - Clarivate的引文数据库（需要订阅）
- [x] **JSTOR** - 学术期刊数字图书馆（无公共API）
- [x] **ResearchGate** - 学术社交网络（无官方API）

**已停止服务：**
- [x] **Microsoft Academic** - 服务已于2021年12月31日停止（占位符实现）

## 📦 安装

`academic-mcp` 可以使用 `uv` 或 `pip` 安装。以下是针对不同场景的详细安装指南。

### ⚡ 快速安装

安装软件包：

```bash
pip install academic-mcp
```

启动 MCP 服务器：

```bash
academic-mcp
```

### 🔧 MCP 客户端配置

选择您使用的 MCP 客户端并按照配置步骤操作：

<details>
<summary><b>1️⃣ Claude Desktop（桌面应用）</b></summary>

**配置文件位置：**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**配置：**
```json
{
  "mcpServers": {
    "academic-mcp": {
      "command": "python",
      "args": ["-m", "academic_mcp"],
      "env": {
        "SEMANTIC_SCHOLAR_API_KEY": "",
        "SCIENCEDIRECT_API_KEY": "",
        "SPRINGER_API_KEY": "",
        "IEEE_API_KEY": "",
        "SCOPUS_API_KEY": "",
        "CORE_API_KEY": "",
        "WOS_API_KEY": "",
        "ACADEMIC_MCP_ENABLED_SOURCES": "arxiv,pubmed,pmc,biorxiv,medrxiv,semantic,core,crossref,google_scholar,iacr",
        "ACADEMIC_MCP_DISABLED_SOURCES": "ieee,scopus,springer,sciencedirect,wos,acm,jstor",
        "ACADEMIC_MCP_DOWNLOAD_PATH": "./downloads"
      }
    }
  }
}
```

</details>

<details>
<summary><b>2️⃣ Claude Code（命令行工具）</b></summary>

**配置文件位置：**
- 用户级：`~/.claude/settings.json`
- 项目级：`.mcp.json`

**配置内容：**
```json
{
  "mcpServers": {
    "academic-mcp": {
      "command": "academic-mcp",
      "args": [],
      "env": {
        "SEMANTIC_SCHOLAR_API_KEY": "",
        "SCIENCEDIRECT_API_KEY": "",
        "SPRINGER_API_KEY": "",
        "IEEE_API_KEY": "",
        "SCOPUS_API_KEY": "",
        "CORE_API_KEY": "",
        "WOS_API_KEY": "",
        "ACADEMIC_MCP_ENABLED_SOURCES": "arxiv,pubmed,pmc,biorxiv,medrxiv,semantic,core,crossref,google_scholar,iacr",
        "ACADEMIC_MCP_DISABLED_SOURCES": "ieee,scopus,springer,sciencedirect,wos,acm,jstor",
        "ACADEMIC_MCP_DOWNLOAD_PATH": "./downloads"
      }
    }
  }
}
```

> **提示：** 你也可以使用 `"command": "python"` 配合 `"args": ["-m", "academic_mcp"]`，如果你更习惯通过 Python 模块运行。

**验证安装：**
```bash
# 检查 academic-mcp 是否已加载
claude mcp list

# 测试服务器
claude mcp test academic-mcp
```

</details>

<details>
<summary><b>3️⃣ Cline（VS Code 扩展）</b></summary>

**配置位置：** VS Code 设置 → 扩展 → Cline → MCP 设置

**方法 1：通过 VS Code 设置界面**
1. 打开 VS Code 设置（Cmd/Ctrl + ,）
2. 搜索 "Cline MCP"
3. 点击 "在 settings.json 中编辑"
4. 添加配置：

```json
{
  "cline.mcpServers": {
    "academic-mcp": {
      "command": "academic-mcp",
      "args": [],
      "env": {
        "SEMANTIC_SCHOLAR_API_KEY": "",
        "SCIENCEDIRECT_API_KEY": "",
        "SPRINGER_API_KEY": "",
        "IEEE_API_KEY": "",
        "SCOPUS_API_KEY": "",
        "CORE_API_KEY": "",
        "WOS_API_KEY": "",
        "ACADEMIC_MCP_ENABLED_SOURCES": "arxiv,pubmed,pmc,biorxiv,medrxiv,semantic,core,crossref,google_scholar,iacr",
        "ACADEMIC_MCP_DISABLED_SOURCES": "ieee,scopus,springer,sciencedirect,wos,acm,jstor",
        "ACADEMIC_MCP_DOWNLOAD_PATH": "./downloads"
      }
    }
  }
}
```

**方法 2：直接编辑 settings.json**

编辑 `~/.config/Code/User/settings.json`（Linux/macOS）或 `%APPDATA%\Code\User\settings.json`（Windows）：

```json
{
  "cline.mcpServers": {
    "academic-mcp": {
      "command": "academic-mcp",
      "args": [],
      "env": {
        "SEMANTIC_SCHOLAR_API_KEY": "",
        "SCIENCEDIRECT_API_KEY": "",
        "SPRINGER_API_KEY": "",
        "IEEE_API_KEY": "",
        "SCOPUS_API_KEY": "",
        "CORE_API_KEY": "",
        "WOS_API_KEY": "",
        "ACADEMIC_MCP_ENABLED_SOURCES": "arxiv,pubmed,pmc,biorxiv,medrxiv,semantic,core,crossref,google_scholar,iacr",
        "ACADEMIC_MCP_DISABLED_SOURCES": "ieee,scopus,springer,sciencedirect,wos,acm,jstor",
        "ACADEMIC_MCP_DOWNLOAD_PATH": "./downloads"
      }
    }
  }
}
```

</details>

<details>
<summary><b>4️⃣ Zed 编辑器</b></summary>

**配置文件位置：** `~/.config/zed/settings.json`

**配置内容：**
```json
{
  "context_servers": {
    "academic-mcp": {
      "command": {
        "path": "academic-mcp",
        "args": []
      },
      "settings": {
        "env": {
          "SEMANTIC_SCHOLAR_API_KEY": "",
          "SCIENCEDIRECT_API_KEY": "",
          "SPRINGER_API_KEY": "",
          "IEEE_API_KEY": "",
          "SCOPUS_API_KEY": "",
          "CORE_API_KEY": "",
          "WOS_API_KEY": "",
          "ACADEMIC_MCP_ENABLED_SOURCES": "arxiv,pubmed,pmc,biorxiv,medrxiv,semantic,core,crossref,google_scholar,iacr",
          "ACADEMIC_MCP_DISABLED_SOURCES": "ieee,scopus,springer,sciencedirect,wos,acm,jstor",
          "ACADEMIC_MCP_DOWNLOAD_PATH": "./downloads"
        }
      }
    }
  }
}
```

</details>

<details>
<summary><b>5️⃣ 自定义 MCP 客户端</b></summary>

对于其他 MCP 客户端，使用标准的 MCP 服务器配置：

**服务器命令：**
```bash
academic-mcp
# 或
python -m academic_mcp
```

**环境变量：**
- `SEMANTIC_SCHOLAR_API_KEY`: Semantic Scholar 的可选 API 密钥
- `SCIENCEDIRECT_API_KEY`: Science Direct 的可选 API 密钥
- `SPRINGER_API_KEY`: Springer Link 的可选 API 密钥
- `IEEE_API_KEY`: IEEE Xplore 的可选 API 密钥
- `SCOPUS_API_KEY`: Scopus 的可选 API 密钥
- `CORE_API_KEY`: CORE 的可选 API 密钥
- `WOS_API_KEY`: Web of Science 的可选 API 密钥
- `ACADEMIC_MCP_DOWNLOAD_PATH`: 下载目录（默认：`./downloads`）
- `ACADEMIC_MCP_ENABLED_SOURCES`: 逗号分隔的启用数据源列表
- `ACADEMIC_MCP_DISABLED_SOURCES`: 逗号分隔的禁用数据源列表

**服务器功能：**
- 工具：`paper_search`、`paper_download`、`paper_read`
- 传输方式：stdio
- 协议：MCP 1.0

</details>

### ⚙️ 环境变量

**API 密钥**（可选 - 仅用于付费服务）：
- `SEMANTIC_SCHOLAR_API_KEY`: Semantic Scholar（[获取 API 密钥](https://www.semanticscholar.org/product/api)）
- `SCIENCEDIRECT_API_KEY`: Elsevier Science Direct（[获取 API 密钥](https://dev.elsevier.com/)）
- `SPRINGER_API_KEY`: Springer Nature（[获取 API 密钥](https://dev.springernature.com/)）
- `IEEE_API_KEY`: IEEE Xplore（[获取 API 密钥](https://developer.ieee.org/)）
- `SCOPUS_API_KEY`: Elsevier Scopus（[获取 API 密钥](https://dev.elsevier.com/)）
- `CORE_API_KEY`: CORE 聚合器（[获取 API 密钥](https://core.ac.uk/services/api)）
- `WOS_API_KEY`: Web of Science（需要机构订阅）

**通用设置：**
- `ACADEMIC_MCP_DOWNLOAD_PATH`: 下载 PDF 的目录（默认：`./downloads`）

**数据源控制：**
- `ACADEMIC_MCP_ENABLED_SOURCES`: 要启用的数据源的逗号分隔列表（白名单）
- `ACADEMIC_MCP_DISABLED_SOURCES`: 要禁用的数据源的逗号分隔列表（黑名单）
- 如果两者都设置，`ACADEMIC_MCP_ENABLED_SOURCES` 优先
- 如果两者都未设置，则默认启用所有 18 个数据源

**可用数据源名称（共 18 个）：**

| 数据源名称 | 类型 | API 密钥要求 | 描述 |
|-----------|------|--------------|------|
| `arxiv` | 免费 | - | 物理、数学、计算机科学预印本库 |
| `pubmed` | 免费 | - | 来自 MEDLINE 的生物医学文献 |
| `pmc` | 免费 | - | PubMed Central 全文存档 |
| `biorxiv` | 免费 | - | 生物学预印本服务器 |
| `medrxiv` | 免费 | - | 健康科学预印本服务器 |
| `google_scholar` | 免费 | - | Google Scholar 搜索 |
| `iacr` | 免费 | - | 国际密码学研究协会 |
| `semantic` | 免费 | `SEMANTIC_SCHOLAR_API_KEY`（可选）<br>[获取 API 密钥](https://www.semanticscholar.org/product/api) | Semantic Scholar AI 驱动搜索（使用 API 密钥可获得更高速率限制） |
| `crossref` | 免费 | - | Crossref DOI 元数据 |
| `core` | 免费 | `CORE_API_KEY`<br>[获取 API 密钥](https://core.ac.uk/services/api) | CORE 开放获取论文聚合器 |
| `ieee` | 付费 | `IEEE_API_KEY`<br>[获取 API 密钥](https://developer.ieee.org/) | IEEE Xplore 数字图书馆 |
| `scopus` | 付费 | `SCOPUS_API_KEY`<br>[获取 API 密钥](https://dev.elsevier.com/) | Elsevier Scopus 数据库 |
| `springer` | 付费 | `SPRINGER_API_KEY`<br>[获取 API 密钥](https://dev.springernature.com/) | Springer 出版物 |
| `sciencedirect` | 付费 | `SCIENCEDIRECT_API_KEY`<br>[获取 API 密钥](https://dev.elsevier.com/) | Elsevier ScienceDirect |
| `wos` | 付费 | `WOS_API_KEY`<br>[机构访问](https://clarivate.com/webofsciencegroup/solutions/web-of-science/) | Web of Science（需要机构订阅） |
| `acm` | 付费 | - | ACM 数字图书馆 |
| `jstor` | 付费 | - | JSTOR 存档 |
| `researchgate` | 免费 | - | ResearchGate 社交网络 |


## 🚀 使用

配置完成后，`academic-mcp` 通过 Claude Desktop 或任何兼容 MCP 的客户端提供三个主要工具。

### 1. 搜索论文 (`paper_search`)

跨多个来源搜索学术论文：

**基础搜索示例：**
```python
# 在 arXiv 上搜索机器学习论文
paper_search([
    {"searcher": "arxiv", "query": "machine learning", "max_results": 5}
])

# 在 PubMed Central 搜索生物医学论文
paper_search([
    {"searcher": "pmc", "query": "cancer treatment", "max_results": 5}
])

# 在 CORE 搜索开放获取论文
paper_search([
    {"searcher": "core", "query": "climate change", "max_results": 5}
])
```

**多平台搜索：**
```python
# 同时搜索多个平台
paper_search([
    {"searcher": "arxiv", "query": "deep learning", "max_results": 5},
    {"searcher": "pubmed", "query": "cancer immunotherapy", "max_results": 3},
    {"searcher": "pmc", "query": "diabetes treatment", "max_results": 3},
    {"searcher": "semantic", "query": "climate change", "max_results": 4, "year": "2020-2023"}
])
```

**付费数据源（需要 API 密钥）：**
```python
# 搜索 IEEE Xplore（需要 IEEE_API_KEY）
paper_search([
    {"searcher": "ieee", "query": "neural networks", "max_results": 5}
])

# 搜索 Springer Link（需要 SPRINGER_API_KEY）
paper_search([
    {"searcher": "springer", "query": "quantum computing", "max_results": 5}
])

# 搜索 Scopus（需要 SCOPUS_API_KEY）
paper_search([
    {"searcher": "scopus", "query": "artificial intelligence", "max_results": 5}
])
```

**搜索所有平台：**
```python
# 搜索所有平台（省略 "searcher" 参数）
paper_search([
    {"query": "quantum computing", "max_results": 10}
])
```

### 2. 下载论文 (`paper_download`)

使用标识符下载论文 PDF：

```python
# 从免费数据源下载
paper_download([
    {"searcher": "arxiv", "paper_id": "2106.12345"},
    {"searcher": "pubmed", "paper_id": "32790614"},
    {"searcher": "pmc", "paper_id": "PMC7419405"},
    {"searcher": "biorxiv", "paper_id": "10.1101/2020.01.01.123456"},
    {"searcher": "semantic", "paper_id": "DOI:10.18653/v1/N18-3011"}
])

# 从 CORE 下载（开放获取）
paper_download([
    {"searcher": "core", "paper_id": "123456789"}
])
```

**注意：** 付费数据源（IEEE、Springer、Science Direct、Scopus）需要机构访问权限或订阅才能下载 PDF。

### 3. 阅读论文 (`paper_read`)

提取和阅读论文的文本内容：

```python
# 从免费数据源阅读论文
paper_read(searcher="arxiv", paper_id="2106.12345")
paper_read(searcher="pubmed", paper_id="32790614")
paper_read(searcher="pmc", paper_id="PMC7419405")
paper_read(searcher="biorxiv", paper_id="10.1101/2020.01.01.123456")
paper_read(searcher="semantic", paper_id="DOI:10.18653/v1/N18-3011")
paper_read(searcher="core", paper_id="123456789")
```

---

### 🛠️ 开发环境

对于想要修改代码或贡献的开发者：

1. **设置环境**：

   ```bash
   # 如果未安装 uv，请先安装
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # 克隆仓库
   git clone https://github.com/LinXueyuanStdio/academic-mcp.git
   cd academic-mcp

   # 创建并激活虚拟环境
   uv venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

2. **安装依赖**：

   ```bash
   # 安装依赖（推荐）
   uv pip install -e .

   # 添加开发依赖（可选）
   uv pip install pytest flake8
   ```

---

## 🤝 贡献

我们欢迎贡献！以下是入门指南：

1. **Fork 仓库**：
   在 GitHub 上点击"Fork"。

2. **克隆并设置**：

   ```bash
   git clone https://github.com/yourusername/academic-mcp.git
   cd academic-mcp
   uv pip install -e .  # 以开发模式安装
   ```

3. **进行更改**：

   - 在 `academic_mcp/sources/` 中添加新平台。
   - 在 `tests/` 中更新测试。

4. **提交 Pull Request**：
   推送更改并在 GitHub 上创建 PR。

## 📄 许可证

本项目采用 MIT 许可证。详情请参阅 LICENSE 文件。

---

祝您使用 `academic-mcp` 研究愉快！如果遇到问题，请在 GitHub 上提交 issue。
