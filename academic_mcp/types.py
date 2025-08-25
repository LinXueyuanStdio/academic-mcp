from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional


@dataclass
class Paper:
    """Standardized paper format with core fields for academic sources"""

    # 核心字段（必填，但允许空值或默认值）
    paper_id: str  # Unique identifier (e.g., arXiv ID, PMID, DOI)
    title: str  # Paper title
    authors: List[str]  # List of author names
    abstract: str  # Abstract text
    doi: str  # Digital Object Identifier
    published_date: datetime  # Publication date
    pdf_url: str  # Direct PDF link
    url: str  # URL to paper page
    source: str  # Source platform (e.g., 'arxiv', 'pubmed')

    # 可选字段
    updated_date: Optional[datetime] = None  # Last updated date
    categories: List[str] = None  # Subject categories
    keywords: List[str] = None  # Keywords
    citations: int = 0  # Citation count
    references: Optional[List[str]] = None  # List of reference IDs/DOIs
    extra: Optional[Dict] = None  # Source-specific extra metadata

    def __post_init__(self):
        """Post-initialization to handle default values"""
        if self.authors is None:
            self.authors = []
        if self.categories is None:
            self.categories = []
        if self.keywords is None:
            self.keywords = []
        if self.references is None:
            self.references = []
        if self.extra is None:
            self.extra = {}

    def to_dict(self) -> Dict:
        """Convert paper to dictionary format for serialization"""
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "authors": "; ".join(self.authors) if self.authors else "",
            "abstract": self.abstract,
            "doi": self.doi,
            "published_date": self.published_date.isoformat() if self.published_date else "",
            "pdf_url": self.pdf_url,
            "url": self.url,
            "source": self.source,
            "updated_date": self.updated_date.isoformat() if self.updated_date else "",
            "categories": "; ".join(self.categories) if self.categories else "",
            "keywords": "; ".join(self.keywords) if self.keywords else "",
            "citations": self.citations,
            "references": "; ".join(self.references) if self.references else "",
            "extra": str(self.extra) if self.extra else "",
        }


def paper2text(paper: Paper) -> str:
    """Convert Paper object to a text representation."""
    texts = []
    if paper.source:
        texts.append(f"Source: '{paper.source}'")
    if paper.paper_id:
        texts.append(f"Paper ID: '{paper.paper_id}'")
    if paper.title:
        texts.append(f"Title: {paper.title}")
    if paper.authors:
        texts.append(f"Authors: {'; '.join(paper.authors)}")
    if paper.abstract:
        texts.append(f"Abstract: {paper.abstract}")
    if paper.published_date:
        texts.append(f"Published Date: {paper.published_date.strftime('%Y-%m-%d')}")
    if paper.url:
        texts.append(f"URL: {paper.url}")
    if paper.doi:
        texts.append(f"DOI: {paper.doi}")
    if paper.categories:
        texts.append(f"Categories: {'; '.join(paper.categories)}")
    if paper.keywords:
        texts.append(f"Keywords: {'; '.join(paper.keywords)}")
    if paper.citations:
        texts.append(f"Citations: {paper.citations}")
    if paper.references:
        texts.append(f"References: {'; '.join(paper.references)}")
    if paper.extra:
        texts.append(f"Extra Info: {paper.extra}")
    if not texts:
        texts.append(str(paper.to_dict()))
    text = "\n".join(texts)
    return text


class PaperSource:
    """Abstract base class for paper sources"""

    def search(self, query: str, **kwargs) -> List[Paper]:
        raise NotImplementedError

    def download_pdf(self, paper_id: str, save_path: str) -> str:
        raise NotImplementedError

    def read_paper(self, paper_id: str, save_path: str) -> str:
        raise NotImplementedError
