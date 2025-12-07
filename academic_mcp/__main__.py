import asyncio
import os
import traceback
from typing import Any, Dict, List, Literal, Optional, cast

import httpx
from loguru import logger
from fastmcp import FastMCP
from mcp.types import TextContent
from pydantic import BaseModel, Field, field_validator, model_validator
import typer

from xlin import xmap_async

from .types import Paper, PaperSource, paper2text
from .sources.arxiv import ArxivSearcher
from .sources.pubmed import PubMedSearcher
from .sources.biorxiv import BioRxivSearcher
from .sources.medrxiv import MedRxivSearcher
from .sources.google_scholar import GoogleScholarSearcher
from .sources.iacr import IACRSearcher
from .sources.semantic import SemanticSearcher
from .sources.crossref import CrossRefSearcher
# from .academic_platforms.hub import SciHubSearcher

# Initialize MCP server
mcp = FastMCP("academic_mcp")

SAVE_PATH = os.getenv("ACADEMIC_MCP_DOWNLOAD_PATH", "./downloads")
os.makedirs(SAVE_PATH, exist_ok=True)

# Instances of searchers
arxiv_searcher = ArxivSearcher()
pubmed_searcher = PubMedSearcher()
biorxiv_searcher = BioRxivSearcher()
medrxiv_searcher = MedRxivSearcher()
google_scholar_searcher = GoogleScholarSearcher()
iacr_searcher = IACRSearcher()
semantic_searcher = SemanticSearcher()
crossref_searcher = CrossRefSearcher()
# scihub_searcher = SciHubSearcher()

engine2searcher: Dict[str, PaperSource] = {
    "arxiv": arxiv_searcher,
    "pubmed": pubmed_searcher,
    "biorxiv": biorxiv_searcher,
    "medrxiv": medrxiv_searcher,
    "google_scholar": google_scholar_searcher,
    "iacr": iacr_searcher,
    "semantic": semantic_searcher,
    "crossref": crossref_searcher,
    # "scihub": scihub_searcher,
}


# region paper_search
class PaperQuery(BaseModel):
    searcher: Optional[Literal["arxiv", "pubmed", "biorxiv", "medrxiv", "google_scholar", "iacr", "semantic", "crossref"]] = Field(
        default=None,
        description="The academic platform to search from. None means searching from all available platforms.",
    )
    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Search query string. Must be between 1 and 500 characters.",
    )
    max_results: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of results to return. Must be between 1 and 100.",
    )
    fetch_details: Optional[bool] = Field(
        default=True,
        description="""[Only applicable to searcher == 'iacr']
Whether to fetch detailed information for each paper.""",
    )
    year: Optional[str] = Field(
        default=None,
        pattern=r"^\d{4}(-\d{4})?|\d{4}-|-\d{4}$",
        description="""[Only applicable to searcher == 'semantic']
Year filter for Semantic Scholar search. Valid formats:
- Single year: '2019'
- Year range: '2016-2020'
- From year onwards: '2010-'
- Up to year: '-2015'""",
    )
    kwargs: Optional[Dict[str, Any]] = Field(
        default=None,
        description="""[Only applicable to searcher == 'crossref']
Additional search parameters:
- filter: CrossRef filter string (e.g., 'has-full-text:true,from-pub-date:2020')
- sort: Sort field ('relevance', 'published', 'updated', 'deposited', etc.)
- order: Sort order ('asc' or 'desc')""",
    )

    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate and clean the query string."""
        v = v.strip()
        if not v:
            raise ValueError("Query cannot be empty or whitespace only")
        return v

    @model_validator(mode='after')
    def validate_searcher_specific_params(self) -> 'PaperQuery':
        """Validate that searcher-specific parameters are only used with appropriate searchers."""
        if self.year is not None and self.searcher not in [None, 'semantic']:
            raise ValueError("'year' parameter is only applicable when searcher is 'semantic' or None")
        if self.kwargs is not None and self.searcher not in [None, 'crossref']:
            raise ValueError("'kwargs' parameter is only applicable when searcher is 'crossref' or None")
        if self.fetch_details is not None and self.fetch_details != True and self.searcher not in [None, 'iacr']:
            raise ValueError("'fetch_details' parameter is only applicable when searcher is 'iacr' or None")
        return self


# Asynchronous helper to adapt synchronous searchers
async def async_search(searcher: PaperSource, query: str, max_results: int, **kwargs) -> List[Paper]:
    async with httpx.AsyncClient() as client:
        # Assuming searchers use requests internally; we'll call synchronously for now
        if 'year' in kwargs:
            papers = searcher.search(query, year=kwargs['year'], max_results=max_results)
        else:
            papers = searcher.search(query, max_results=max_results)
        return papers

def expand_query(query_list: list[PaperQuery]) -> list[PaperQuery]:
    expanded_queries = []
    for query in query_list:
        if query.searcher:
            expanded_queries.append(query)
        else:
            # Expand to all available platforms
            for engine in engine2searcher.keys():
                expanded_query = query.model_copy(update={"searcher": engine})
                expanded_queries.append(expanded_query)
    return expanded_queries

async def async_search_per_query(query: PaperQuery) -> List[Paper]:
    searcher = engine2searcher.get(query.searcher)
    if not searcher:
        return []
    papers = []
    if query.searcher == "iacr":
        papers = iacr_searcher.search(query.query, query.max_results, query.fetch_details)
    elif query.searcher == "semantic":
        papers = semantic_searcher.search(query.query, query.year, query.max_results)
    elif query.searcher == "crossref":
        kwargs = query.kwargs if query.kwargs else {}
        papers = crossref_searcher.search(query.query, query.max_results, **kwargs)
    else:
        papers = await async_search(searcher, query.query, query.max_results)
    return papers


async def async_search_per_query_list(query_list: List[PaperQuery]) -> List[Paper]:
    all_papers = await asyncio.gather(*[async_search_per_query(query) for query in query_list])
    papers = sum(all_papers, [])
    return papers


@mcp.tool(
    name="paper_search",
    description="""Search academic papers from multiple sources.

## Available sources: arxiv, PubMed, bioRxiv, medRxiv, Google Scholar, IACR ePrint Archive, Semantic Scholar, CrossRef.

## Input Constraints:
- query: 1-500 characters, required, cannot be empty
- max_results: 1-100, default is 10
- year: Valid formats: '2019', '2016-2020', '2010-', '-2015' (only for semantic)
- fetch_details: boolean (only for iacr)
- kwargs: dict (only for crossref)

## Example:
paper_search([
    {"searcher": "arxiv", "query": "machine learning", "max_results": 5},
    {"searcher": "pubmed", "query": "cancer immunotherapy", "max_results": 3},
    {"searcher": "iacr", "query": "cryptography", "max_results": 3, "fetch_details": true},
    {"searcher": "semantic", "query": "climate change", "max_results": 4, "year": "2015-2020"},
    {"searcher": "crossref", "query": "deep learning", "max_results": 2, "kwargs": {"filter": "from-pub-date:2020,has-full-text:true"}},
    {"query": "deep learning", "max_results": 2}
])
""",
)
async def paper_search(query_list: List[PaperQuery]) -> Dict[str, List[TextContent]]:
    async with httpx.AsyncClient() as client:
        expanded_queries = expand_query(query_list)
        papers = await xmap_async(expanded_queries, async_search_per_query_list, is_async_work_func=True, desc="Searching papers", is_batch_work_func=True, batch_size=1)
        texts = []
        for paper in papers:
            if isinstance(paper, dict) and "error" in paper:
                pass
            else:
                texts.append(paper2text(cast(Paper, paper)))
        content = "\n\n".join(texts) if texts else "No papers found."
        return content
    content = "No papers found."
    return content

# endregion paper_search


# region paper_download

class PaperDownloadQuery(BaseModel):
    searcher: Literal["arxiv", "pubmed", "biorxiv", "medrxiv", "google_scholar", "iacr", "semantic", "crossref"] = Field(
        description="The academic platform to download from."
    )
    paper_id: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="""The unique identifier of the paper to download. Format depends on the searcher:
- arxiv: arXiv ID (e.g., '2106.12345')
- pubmed: PubMed ID/PMID (e.g., '32790614')
- biorxiv: bioRxiv DOI (e.g., '10.1101/2020.01.01.123456')
- medrxiv: medRxiv DOI (e.g., '10.1101/2020.01.01.123456')
- iacr: IACR paper ID (e.g., '2009/101')
- semantic: Semantic Scholar ID or prefixed ID (e.g., 'DOI:10.18653/v1/N18-3011', 'ARXIV:2106.15928')
- crossref: DOI (e.g., '10.1038/s41586-020-2649-2')"""
    )

    @field_validator('paper_id')
    @classmethod
    def validate_paper_id(cls, v: str) -> str:
        """Validate and clean the paper ID."""
        v = v.strip()
        if not v:
            raise ValueError("Paper ID cannot be empty or whitespace only")
        return v


async def async_download_per_query(query: PaperDownloadQuery) -> str:
    searcher = engine2searcher.get(query.searcher)
    if not searcher:
        return f"Searcher '{query.searcher}' not found."
    try:
        pdf_path = searcher.download_pdf(query.paper_id, SAVE_PATH)
        return pdf_path
    except Exception as e:
        logger.error(f"Error downloading paper {query.paper_id} from {query.searcher}: {e}\n{traceback.format_exc()}")
        return f"Error downloading paper {query.paper_id} from {query.searcher}: {e}"

@mcp.tool(
    name="paper_download",
    description="""Download academic paper PDFs from multiple sources.

## Input Constraints:
- searcher: Required, must be one of the supported platforms
- paper_id: Required, 1-200 characters, cannot be empty

## Paper ID formats:
- arXiv: Use the arXiv ID (e.g., "2106.12345").
- PubMed: Use the PubMed ID (PMID) (e.g., "32790614").
- bioRxiv: Use the bioRxiv DOI (e.g., "10.1101/2020.01.01.123456").
- medRxiv: Use the medRxiv DOI (e.g., "10.1101/2020.01.01.123456").
- Google Scholar: Direct PDF download is not supported; please use the paper URL to access the publisher's website.
- IACR: Use the IACR paper ID (e.g., "2009/101").
- Semantic Scholar: Use the Semantic Scholar paper ID, Paper identifier in one of the following formats:
    - Semantic Scholar ID (e.g., "649def34f8be52c8b66281af98ae884c09aef38b")
    - DOI:<doi> (e.g., "DOI:10.18653/v1/N18-3011")
    - ARXIV:<id> (e.g., "ARXIV:2106.15928")
    - MAG:<id> (e.g., "MAG:112218234")
    - ACL:<id> (e.g., "ACL:W12-3903")
    - PMID:<id> (e.g., "PMID:19872477")
    - PMCID:<id> (e.g., "PMCID:2323736")
    - URL:<url> (e.g., "URL:https://arxiv.org/abs/2106.15928v1")

## Returns:
List of paths to the downloaded PDF files.

## Example:
paper_download([
    {"searcher": "arxiv", "paper_id": "2106.12345"},
    {"searcher": "pubmed", "paper_id": "32790614"},
    {"searcher": "biorxiv", "paper_id": "10.1101/2020.01.01.123456"},
    {"searcher": "semantic", "paper_id": "DOI:10.18653/v1/N18-3011"}
])
""",
)
async def paper_download(query_list: List[PaperDownloadQuery]) -> List[str]:
    async with httpx.AsyncClient() as client:
        pdf_paths = await xmap_async(query_list, async_download_per_query, is_async_work_func=True, desc="Downloading papers")
        return pdf_paths
    return []
# endregion paper_download


# region paper_read
@mcp.tool(
    name="paper_read",
    description="""Read and extract text content from academic paper PDFs from multiple sources.

## Input Constraints:
- searcher: Required, must be one of: arxiv, pubmed, biorxiv, medrxiv, iacr, semantic, crossref
- paper_id: Required, 1-200 characters, cannot be empty

## Example:

### arXiv
paper_read({"searcher": "arxiv", "paper_id": "2106.12345", "save_path": "./downloads"})  # paper_id is arXiv ID.
### PubMed
paper_read({"searcher": "pubmed", "paper_id": "32790614", "save_path": "./downloads"})  # paper_id is PubMed ID (PMID).
### bioRxiv
paper_read({"searcher": "biorxiv", "paper_id": "10.1101/2020.01.01.123456", "save_path": "./downloads"})  # paper_id is bioRxiv DOI.
### medRxiv
paper_read({"searcher": "medrxiv", "paper_id": "10.1101/2020.01.01.123456", "save_path": "./downloads"})  # paper_id is medRxiv DOI.
### IACR
paper_read({"searcher": "iacr", "paper_id": "2009/101", "save_path": "./downloads"})  # paper_id is IACR paper ID.
### Semantic Scholar
paper_read({"searcher": "semantic", "paper_id": "DOI:10.18653/v1/N18-3011", "save_path": "./downloads"})
where paper_id: Semantic Scholar paper ID, Paper identifier in one of the following formats:
    - Semantic Scholar ID (e.g., "649def34f8be52c8b66281af98ae884c09aef38b")
    - DOI:<doi> (e.g., "DOI:10.18653/v1/N18-3011")
    - ARXIV:<id> (e.g., "ARXIV:2106.15928")
    - MAG:<id> (e.g., "MAG:112218234")
    - ACL:<id> (e.g., "ACL:W12-3903")
    - PMID:<id> (e.g., "PMID:19872477")
    - PMCID:<id> (e.g., "PMCID:2323736")
    - URL:<url> (e.g., "URL:https://arxiv.org/abs/2106.15928v1")
### CrossRef
paper_read({"searcher": "crossref", "paper_id": "10.1038/s41586-020-2649-2", "save_path": "./downloads"})  # paper_id is DOI.
""")
async def paper_read(
    searcher: Literal["arxiv", "pubmed", "biorxiv", "medrxiv", "iacr", "semantic", "crossref"],
    paper_id: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="The unique identifier of the paper to read (format depends on searcher)"
    ),
) -> str:
    try:
        # Validate paper_id
        paper_id = paper_id.strip()
        if not paper_id:
            return "Error: paper_id cannot be empty or whitespace only"

        searcher_instance = engine2searcher.get(searcher)
        if not searcher_instance:
            return f"Searcher '{searcher}' not found or not supported."
        text = searcher_instance.read_paper(paper_id, SAVE_PATH)
        return text
    except Exception as e:
        logger.error(f"Error converting paper to text: {e}\n{traceback.format_exc()}")
        return f"Error converting paper to text: {e}"

# endregion paper_read



app = typer.Typer(add_completion=False)


@app.callback(invoke_without_command=True)
def run(
    host: str = typer.Option("127.0.0.1", help="Bind host (SSE/HTTP only)."),
    port: int = typer.Option(8000, min=1, max=65535, help="Bind port (SSE/HTTP only)."),
    debug: bool = typer.Option(False, help="Enable debug logging."),
    transport: Optional[Literal["stdio", "sse", "streamable-http", "http"]] = typer.Option(
        None,
        "--transport",
        "-t",
        help="Transport method. One of: stdio, sse, streamable-http, http. Default is stdio; if host/port are set, defaults to sse.",
    ),
) -> None:
    """运行 Academic MCP 服务器。

    默认使用 stdio（适配 MCP 客户端）。如需网络服务（SSE/HTTP），设置环境变量：
    - `ACADEMIC_MCP_TRANSPORT=sse` 或 `ACADEMIC_MCP_TRANSPORT=streamable-http`
    """
    log_level = "debug" if debug else "info"

    if not transport or transport == "stdio":
        logger.info("Starting Academic MCP server with stdio transport")
        mcp.run(transport="stdio", log_level=log_level)
        return

    logger.info(f"Starting Academic MCP server on {host}:{port} with transport '{transport}'")
    mcp.run(transport=transport, host=host, port=port, log_level=log_level)


def main() -> None:
    """Console script entrypoint."""
    app()


if __name__ == "__main__":
    main()