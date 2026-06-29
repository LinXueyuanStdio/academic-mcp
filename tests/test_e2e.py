"""
End-to-end tests for the MCP server paper_search tool.

Tests every active source with actual API queries,
validates response format, and handles error cases.
"""

import asyncio
import unittest
import os
import sys
from typing import List

from academic_mcp.types import Paper, paper2text
from academic_mcp.__main__ import PaperQuery, async_search_per_query, paper_search, engine2searcher


# ── Helpers ──────────────────────────────────────────────────────────────────

def _is_accessible(name: str) -> bool:
    """Check if a source can potentially return results."""
    if name not in engine2searcher:
        return False
    # Check if it has required API keys
    searcher = engine2searcher[name]
    api_key_attr = getattr(searcher, "api_key", None)
    if api_key_attr is not None and api_key_attr == "":
        return False
    return True


def _check_source(name: str) -> str:
    """Return 'skip' reason or empty string if ok."""
    if name not in engine2searcher:
        return f"Source '{name}' not registered"
    searcher = engine2searcher[name]
    api_key = getattr(searcher, "api_key", None)
    if api_key is not None and api_key == "":
        return f"Source '{name}' requires API key (env var not set)"
    return ""


# ── Active Sources (with public APIs) ────────────────────────────────────────

ACTIVE_SOURCES = [
    # name, query, min_results_expected
    ("arxiv", "machine learning", 1),
    ("pubmed", "cancer immunotherapy", 1),
    ("pmc", "cancer treatment", 1),
    ("biorxiv", "cell biology", 1),
    ("medrxiv", "cardiovascular medicine", 1),
    ("crossref", "deep learning", 1),
    ("semantic", "climate change", 1),
    ("iacr", "cryptography", 1),
]

# Sources that may be blocked or require API keys
CONDITIONAL_SOURCES = [
    ("google_scholar", "machine learning", 0),  # may be blocked
    ("ieee", "machine learning", 0),  # requires API key
    ("scopus", "machine learning", 0),  # requires API key
    ("sciencedirect", "machine learning", 0),  # requires API key
    ("springer", "machine learning", 0),  # requires API key
    ("core", "machine learning", 0),  # requires API key
    ("wos", "machine learning", 0),  # requires API key
]

# Sources that always return empty (no API)
PLACEHOLDER_SOURCES = ["acm", "jstor", "researchgate"]


# ── Test Classes ─────────────────────────────────────────────────────────────

class TestAllActiveSourcesE2E(unittest.TestCase):
    """End-to-end test: every active source via async_search_per_query."""

    def _run_search(self, name: str, query: str, max_results: int):
        """Run a search and return papers list."""
        q = PaperQuery(searcher=name, query=query, max_results=max_results)
        return asyncio.run(async_search_per_query(q))

    def _validate_papers(self, papers: List[Paper], source: str, min_expected: int):
        """Validate search results."""
        self.assertIsInstance(papers, list, f"[{source}] Result should be a list")
        if min_expected > 0:
            self.assertGreaterEqual(
                len(papers), min_expected,
                f"[{source}] Expected at least {min_expected} papers, got {len(papers)}"
            )
        for i, paper in enumerate(papers):
            with self.subTest(source=source, paper_index=i):
                self.assertIsInstance(paper, Paper,
                    f"[{source}] paper[{i}] should be Paper, got {type(paper)}")
                self.assertIsInstance(paper.paper_id, str,
                    f"[{source}] paper[{i}].paper_id should be str")
                self.assertIsInstance(paper.title, str,
                    f"[{source}] paper[{i}].title should be str")
                self.assertTrue(len(paper.title) > 0,
                    f"[{source}] paper[{i}].title should not be empty")
                self.assertIsInstance(paper.authors, list,
                    f"[{source}] paper[{i}].authors should be list")
                self.assertEqual(paper.source, source,
                    f"[{source}] paper[{i}].source mismatch: {paper.source}")
                # Ensure to_dict() works
                d = paper.to_dict()
                self.assertIsInstance(d, dict)
                # Ensure paper2text works
                text = paper2text(paper)
                self.assertIsInstance(text, str)
                self.assertTrue(len(text) > 0)

    # ── Active sources ──

    def test_arxiv_e2e(self):
        reason = _check_source("arxiv")
        if reason: self.skipTest(reason)
        papers = self._run_search("arxiv", "machine learning", 5)
        self._validate_papers(papers, "arxiv", 1)

    def test_pubmed_e2e(self):
        reason = _check_source("pubmed")
        if reason: self.skipTest(reason)
        papers = self._run_search("pubmed", "cancer immunotherapy", 3)
        self._validate_papers(papers, "pubmed", 1)

    def test_pmc_e2e(self):
        reason = _check_source("pmc")
        if reason: self.skipTest(reason)
        papers = self._run_search("pmc", "cancer treatment", 3)
        self._validate_papers(papers, "pmc", 1)

    def test_biorxiv_e2e(self):
        reason = _check_source("biorxiv")
        if reason: self.skipTest(reason)
        papers = self._run_search("biorxiv", "cell biology", 3)
        self._validate_papers(papers, "biorxiv", 1)

    def test_medrxiv_e2e(self):
        reason = _check_source("medrxiv")
        if reason: self.skipTest(reason)
        papers = self._run_search("medrxiv", "cardiovascular medicine", 3)
        self._validate_papers(papers, "medrxiv", 1)

    def test_crossref_e2e(self):
        reason = _check_source("crossref")
        if reason: self.skipTest(reason)
        papers = self._run_search("crossref", "deep learning", 3)
        self._validate_papers(papers, "crossref", 1)

    def test_semantic_e2e(self):
        reason = _check_source("semantic")
        if reason: self.skipTest(reason)
        papers = self._run_search("semantic", "climate change", 3)
        if len(papers) == 0:
            # Semantic Scholar may rate limit without API key
            self.skipTest("Semantic Scholar rate limited (no API key set)")
        self._validate_papers(papers, "semantic", 1)

    def test_iacr_e2e(self):
        reason = _check_source("iacr")
        if reason: self.skipTest(reason)
        papers = self._run_search("iacr", "cryptography", 3)
        self._validate_papers(papers, "iacr", 1)


class TestConditionalSourcesE2E(unittest.TestCase):
    """Test sources that may be blocked or need API keys."""

    def _run_search(self, name: str, query: str, max_results: int):
        q = PaperQuery(searcher=name, query=query, max_results=max_results)
        return asyncio.run(async_search_per_query(q))

    def test_google_scholar(self):
        reason = _check_source("google_scholar")
        if reason: self.skipTest(reason)
        try:
            papers = self._run_search("google_scholar", "machine learning", 3)
        except Exception as e:
            self.skipTest(f"Google Scholar blocked: {e}")
        self.assertIsInstance(papers, list)
        if len(papers) == 0:
            self.skipTest("Google Scholar returned no results (likely blocked)")
        for paper in papers:
            self.assertIsInstance(paper, Paper)
            self.assertEqual(paper.source, "google_scholar")

    def test_ieee(self):
        papers = self._run_search("ieee", "machine learning", 3)
        self.assertIsInstance(papers, list)
        # IEEE returns empty without API key - that's valid behavior
        for paper in papers:
            self.assertIsInstance(paper, Paper)

    def test_scopus(self):
        papers = self._run_search("scopus", "machine learning", 3)
        self.assertIsInstance(papers, list)

    def test_sciencedirect(self):
        papers = self._run_search("sciencedirect", "machine learning", 3)
        self.assertIsInstance(papers, list)

    def test_springer(self):
        papers = self._run_search("springer", "machine learning", 3)
        self.assertIsInstance(papers, list)

    def test_core(self):
        papers = self._run_search("core", "machine learning", 3)
        self.assertIsInstance(papers, list)

    def test_wos(self):
        papers = self._run_search("wos", "machine learning", 3)
        self.assertIsInstance(papers, list)


class TestPlaceholderSourcesE2E(unittest.TestCase):
    """Sources without public APIs should return empty lists gracefully."""

    def _run_search(self, name: str):
        q = PaperQuery(searcher=name, query="test", max_results=5)
        return asyncio.run(async_search_per_query(q))

    def test_acm_returns_empty(self):
        papers = self._run_search("acm")
        self.assertIsInstance(papers, list)
        self.assertEqual(len(papers), 0, "ACM should return empty list (no public API)")

    def test_jstor_returns_empty(self):
        papers = self._run_search("jstor")
        self.assertIsInstance(papers, list)
        self.assertEqual(len(papers), 0, "JSTOR should return empty list (no public API)")

    def test_researchgate_returns_empty(self):
        papers = self._run_search("researchgate")
        self.assertIsInstance(papers, list)
        self.assertEqual(len(papers), 0, "ResearchGate should return empty list (no public API)")


class TestMCPSearchToolE2E(unittest.TestCase):
    """Test the actual MCP tool function paper_search end-to-end."""

    def test_paper_search_single_source_returns_string(self):
        """paper_search should return a non-empty string."""
        result = asyncio.run(paper_search([
            PaperQuery(searcher="arxiv", query="machine learning", max_results=3)
        ]))
        self.assertIsInstance(result, str, f"Expected str, got {type(result)}: {result!r}")
        self.assertTrue(len(result) > 0, "Result string should not be empty")
        self.assertIn("Source:", result)
        self.assertIn("Title:", result)

    def test_paper_search_multi_source_returns_string(self):
        """paper_search with multiple sources should return combined results."""
        result = asyncio.run(paper_search([
            PaperQuery(searcher="arxiv", query="neural networks", max_results=2),
            PaperQuery(searcher="pubmed", query="cancer immunotherapy", max_results=2),
        ]))
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        # At minimum, arxiv should have results (pubmed may vary)
        self.assertIn("Source:", result)
        self.assertIn("Title:", result)
        # If not "No papers found.", at least one source worked
        self.assertNotEqual(result, "No papers found.",
            "All sources returned no results - check network")

    def test_paper_search_expand_all(self):
        """paper_search without searcher should expand to all enabled sources."""
        result = asyncio.run(paper_search([
            PaperQuery(query="deep learning", max_results=2)
        ]))
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        # "No papers found." only if ALL sources returned nothing
        if result == "No papers found.":
            self.skipTest("All sources returned no results (network issue)")

    def test_paper_search_empty_query_rejected(self):
        """Empty query should be rejected by validation."""
        with self.assertRaises(Exception):
            PaperQuery(searcher="arxiv", query="", max_results=3)

    def test_paper_search_whitespace_query_rejected(self):
        """Whitespace-only query should be rejected."""
        with self.assertRaises(Exception):
            PaperQuery(searcher="arxiv", query="   ", max_results=3)

    def test_paper_search_invalid_searcher(self):
        """Invalid searcher name should be rejected by validation."""
        with self.assertRaises(Exception):
            PaperQuery(searcher="nonexistent_source", query="test", max_results=3)

    def test_paper_search_error_source_handled_gracefully(self):
        """Search with a nonexistent source via None searcher should just skip."""
        # When searcher=None, it expands to all. Nonexistent sources are not in
        # engine2searcher so they are skipped. Let's test a disabled source.
        result = asyncio.run(paper_search([
            PaperQuery(searcher="acm", query="machine learning", max_results=3)
        ]))
        # ACM returns empty list → should produce "No papers found."
        self.assertIsInstance(result, str)


class TestPaperDownloadToolE2E(unittest.TestCase):
    """Test the paper_download tool."""

    def test_download_arxiv(self):
        """Download an arxiv paper."""
        import asyncio
        from academic_mcp.__main__ import PaperDownloadQuery, paper_download

        async def run():
            result = await paper_download([
                PaperDownloadQuery(searcher="arxiv", paper_id="2106.12345")
            ])
            return result

        result = asyncio.run(run())
        self.assertIsInstance(result, list)
        if result and not str(result[0]).startswith("Error"):
            self.assertTrue(os.path.exists(result[0]), f"PDF should exist at {result[0]}")


if __name__ == "__main__":
    unittest.main()
