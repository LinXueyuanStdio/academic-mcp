from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
import os
from PyPDF2 import PdfReader
from loguru import logger

from ..types import Paper, PaperSource


class WOSSearcher(PaperSource):
    """Searcher for Web of Science papers via the WoS Starter API.

    Uses the Clarivate Web of Science Starter API (v1).
    Requires API key from https://developer.clarivate.com/apis/wos-starter
    Set environment variable: WOS_API_KEY

    Supported field tags for advanced search queries:
    TS, TI, AU, PY, SO, DO, UT, PMID, OG, FPY, DOP, DT, AI, IS, VL, PG, CS, SUR

    If the query does not begin with a known field tag, it is automatically
    wrapped in TS=(...) for a topic search (title + abstract + keywords).
    """

    BASE_URL = "https://api.clarivate.com/apis/wos-starter/v1"

    _FIELD_TAGS = frozenset(
        "TS= TI= AU= PY= SO= DO= UT= PMID= OG= "
        "FPY= DOP= DT= AI= IS= VL= PG= CS= SUR=".split()
    )

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('WOS_API_KEY', '')
        if not self.api_key:
            logger.warning(
                "Web of Science API key not set. "
                "Set WOS_API_KEY environment variable or obtain a key from "
                "https://developer.clarivate.com/apis/wos-starter"
            )

    def search(self, query: str, max_results: int = 10) -> List[Paper]:
        if not self.api_key:
            logger.error("API key required for Web of Science search")
            return []

        search_expr = self._build_search_expression(query)
        limit = max(1, min(max_results, 50))

        headers = {
            "X-ApiKey": self.api_key,
            "Accept": "application/json",
        }
        params = {
            "q": search_expr,
            "limit": limit,
            "page": 1,
            "sortField": "RS+D",
        }

        try:
            resp = requests.get(
                f"{self.BASE_URL}/documents",
                headers=headers,
                params=params,
                timeout=30,
            )

            if resp.status_code == 401:
                logger.error(
                    "WoS API authentication failed. "
                    "Verify your WOS_API_KEY at https://developer.clarivate.com"
                )
                return []
            if resp.status_code == 404:
                return []

            resp.raise_for_status()
            data = resp.json()

            papers: List[Paper] = []
            for hit in data.get("hits", []):
                try:
                    paper = self._parse_document(hit)
                    if paper is not None:
                        papers.append(paper)
                except Exception:
                    logger.warning(f"Error parsing WoS document {hit.get('uid', '?')}")

            logger.info(
                f"WoS search returned {len(papers)} papers "
                f"(total available: {data.get('metadata', {}).get('total', 0)})"
            )
            return papers

        except requests.RequestException as e:
            logger.error(f"Error searching Web of Science: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in WoS search: {e}")
            return []

    def download_pdf(self, paper_id: str, save_path: str) -> str:
        raise NotImplementedError(
            "Web of Science Starter API does not provide PDF downloads. "
            "Use the record URL to access the paper via your institutional subscription."
        )

    def read_paper(self, paper_id: str, save_path: str = "./downloads") -> str:
        pdf_path = os.path.join(save_path, f"{paper_id}.pdf")

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(
                f"PDF not found: {pdf_path}. "
                "The WoS Starter API is metadata-only; PDFs must be "
                "downloaded via institutional access separately."
            )

        try:
            reader = PdfReader(pdf_path)
            text = "".join(page.extract_text() + "\n" for page in reader.pages)
            return text.strip()
        except Exception as e:
            logger.error(f"Error reading PDF for {paper_id}: {e}")
            return ""

    @classmethod
    def _build_search_expression(cls, query: str) -> str:
        upper = query.strip().upper()
        if any(upper.startswith(tag) for tag in cls._FIELD_TAGS):
            return query
        return f"TS=({query})"

    @staticmethod
    def _parse_date(year: int, month_str: str) -> datetime:
        _MONTH = {
            "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4,
            "MAY": 5, "JUN": 6, "JUL": 7, "AUG": 8,
            "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12,
        }
        month = _MONTH.get(month_str.upper() if month_str else "", 1)
        year = year or 1970
        return datetime(year, month, 1)

    def _parse_document(self, doc: Dict[str, Any]) -> Optional[Paper]:
        try:
            uid = doc.get("uid", "")
            title = doc.get("title", "")

            authors: List[str] = []
            for a in doc.get("names", {}).get("authors", []):
                name = a.get("displayName", "")
                if name:
                    authors.append(name)

            identifiers = doc.get("identifiers", {})

            links = doc.get("links", {})
            record_url = links.get("record", "")

            source = doc.get("source", {})
            pub_year = source.get("publishYear", 0)
            pub_month = source.get("publishMonth", "")
            published_date = self._parse_date(pub_year, pub_month)

            citations = 0
            for c in doc.get("citations", []):
                if c.get("db") == "WOS":
                    citations = c.get("count", 0)
                    break

            keywords = list(doc.get("keywords", {}).get("authorKeywords", []))
            categories = list(doc.get("types", []))

            source_title = source.get("sourceTitle", "")
            volume = source.get("volume", "")
            issue = source.get("issue", "")
            pages = source.get("pages", {})

            return Paper(
                paper_id=uid,
                title=title,
                authors=authors,
                abstract="",
                doi=identifiers.get("doi", ""),
                published_date=published_date,
                pdf_url="",
                url=record_url,
                source="wos",
                categories=categories,
                keywords=keywords,
                citations=citations,
                extra={
                    "source_title": source_title,
                    "volume": volume,
                    "issue": issue,
                    "pages": pages.get("range", ""),
                    "document_types": list(doc.get("sourceTypes", [])),
                },
            )

        except Exception as e:
            logger.error(f"Error parsing WoS document: {e}")
            return None


if __name__ == "__main__":
    # Test WOSSearcher
    searcher = WOSSearcher()

    # Test search
    print("Testing search functionality...")
    query = "machine learning"
    max_results = 5
    try:
        papers = searcher.search(query, max_results=max_results)
        print(f"Found {len(papers)} papers for query '{query}':")
        for i, paper in enumerate(papers, 1):
            print(f"{i}. {paper.title} (ID: {paper.paper_id})")
            print(f"   Authors: {'; '.join(paper.authors[:3])}")
            print(f"   Citations: {paper.citations}, DOI: {paper.doi}")
            print()
    except Exception as e:
        print(f"Error during search: {e}")
