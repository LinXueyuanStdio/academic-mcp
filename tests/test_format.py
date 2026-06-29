"""
Comprehensive tests for return format correctness across all sources.

Tests cover:
1. Paper.to_dict() format validation
2. paper2text null-safety and error resilience
3. Mocked MCP tool response format
"""

import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

from academic_mcp.types import Paper, paper2text


class TestPaperDictFormat(unittest.TestCase):
    """Test that Paper.to_dict() always returns a valid dict with proper types."""

    def test_to_dict_all_fields_present(self):
        """All expected keys should be present in to_dict output."""
        paper = Paper(
            paper_id="test123",
            title="Test Paper",
            authors=["Author One", "Author Two"],
            abstract="This is a test abstract.",
            doi="10.1234/test",
            published_date=datetime(2024, 1, 15),
            pdf_url="https://example.com/test.pdf",
            url="https://example.com/test",
            source="test_source",
        )
        d = paper.to_dict()
        expected_keys = {
            "paper_id", "title", "authors", "abstract", "doi",
            "published_date", "pdf_url", "url", "source",
            "updated_date", "categories", "keywords", "citations",
            "references", "extra",
        }
        self.assertTrue(expected_keys.issubset(d.keys()), f"Missing keys: {expected_keys - d.keys()}")

    def test_to_dict_default_values(self):
        """Default values should be properly serialized."""
        paper = Paper(
            paper_id="test123",
            title="Test",
            authors=[],
            abstract="",
            doi="",
            published_date=datetime(2024, 1, 1),
            pdf_url="",
            url="",
            source="test",
        )
        d = paper.to_dict()
        self.assertEqual(d["paper_id"], "test123")
        self.assertEqual(d["title"], "Test")
        self.assertEqual(d["authors"], "")  # empty list → empty string
        self.assertEqual(d["abstract"], "")
        self.assertEqual(d["doi"], "")
        self.assertEqual(d["citations"], 0)
        self.assertEqual(d["updated_date"], "")  # None → empty string
        self.assertEqual(d["categories"], "")
        self.assertEqual(d["keywords"], "")
        self.assertEqual(d["references"], "")
        self.assertEqual(d["extra"], "")

    def test_to_dict_all_values_are_strings_or_numbers(self):
        """All to_dict values should be JSON-serializable (str/int)."""
        paper = Paper(
            paper_id="test123",
            title="Test Paper",
            authors=["Author One"],
            abstract="Abstract here.",
            doi="10.1234/test",
            published_date=datetime(2024, 6, 15),
            pdf_url="https://example.com/test.pdf",
            url="https://example.com/test",
            source="test_source",
            updated_date=datetime(2024, 7, 1),
            categories=["cat1", "cat2"],
            keywords=["kw1", "kw2"],
            citations=42,
            references=["ref1", "ref2"],
            extra={"key": "value", "nested": {"a": 1}},
        )
        d = paper.to_dict()
        for key, value in d.items():
            self.assertIsInstance(value, (str, int), f"Key '{key}' has type {type(value)}: {value!r}")

    def test_to_dict_authors_semicolon_join(self):
        """Authors list should be joined with '; '."""
        paper = Paper(
            paper_id="test",
            title="Test",
            authors=["Smith, John", "Doe, Jane", "Lee, Bob"],
            abstract="",
            doi="",
            published_date=datetime(2024, 1, 1),
            pdf_url="",
            url="",
            source="test",
        )
        self.assertEqual(paper.to_dict()["authors"], "Smith, John; Doe, Jane; Lee, Bob")

    def test_to_dict_published_date_isoformat(self):
        """published_date should be ISO format string."""
        paper = Paper(
            paper_id="test",
            title="Test",
            authors=[],
            abstract="",
            doi="",
            published_date=datetime(2024, 3, 15, 10, 30, 0),
            pdf_url="",
            url="",
            source="test",
        )
        self.assertTrue(paper.to_dict()["published_date"].startswith("2024-03-15"))

    def test_to_dict_extra_stringified(self):
        """extra dict should be stringified."""
        paper = Paper(
            paper_id="test",
            title="Test",
            authors=[],
            abstract="",
            doi="",
            published_date=datetime(2024, 1, 1),
            pdf_url="",
            url="",
            source="test",
            extra={"journal": "Nature", "volume": "500"},
        )
        d = paper.to_dict()
        self.assertIsInstance(d["extra"], str)


class TestPaper2TextNullSafety(unittest.TestCase):
    """Test that paper2text handles all edge cases without crashing."""

    def _make_minimal_paper(self, **overrides):
        """Create a minimal valid paper with optional overrides."""
        defaults = {
            "paper_id": "test123",
            "title": "Test Paper",
            "authors": ["Author"],
            "abstract": "Abstract.",
            "doi": "",
            "published_date": datetime(2024, 1, 1),
            "pdf_url": "",
            "url": "",
            "source": "test",
        }
        defaults.update(overrides)
        return Paper(**defaults)

    def test_normal_paper(self):
        """Normal paper should produce non-empty text."""
        paper = self._make_minimal_paper()
        text = paper2text(paper)
        self.assertIn("Source: 'test'", text)
        self.assertIn("Paper ID: 'test123'", text)
        self.assertIn("Title: Test Paper", text)
        self.assertIn("Authors: Author", text)

    def test_paper_with_none_published_date(self):
        """Published date being None should not crash."""
        paper = self._make_minimal_paper(published_date=None)
        text = paper2text(paper)
        self.assertIsInstance(text, str)
        self.assertNotIn("Published Date:", text)

    def test_paper_with_string_published_date(self):
        """Published date as string (wrong type) should not crash."""
        paper = self._make_minimal_paper()
        # Bypass type checking to simulate bad data
        object.__setattr__(paper, "published_date", "2024-01-01")
        text = paper2text(paper)
        self.assertIsInstance(text, str)

    def test_paper_with_int_published_date(self):
        """Published date as int (wrong type) should not crash."""
        paper = self._make_minimal_paper()
        object.__setattr__(paper, "published_date", 2024)
        text = paper2text(paper)
        self.assertIsInstance(text, str)

    def test_paper_all_none_fields(self):
        """Paper with all optional fields as None/empty should not crash."""
        paper = Paper(
            paper_id="test",
            title="Test",
            authors=[],
            abstract="",
            doi="",
            published_date=None,
            pdf_url="",
            url="",
            source="",
            updated_date=None,
            categories=None,
            keywords=None,
            citations=0,
            references=None,
            extra=None,
        )
        text = paper2text(paper)
        self.assertIsInstance(text, str)
        self.assertIn("test", text)

    def test_paper_empty_title(self):
        """Empty title should not appear in output."""
        paper = self._make_minimal_paper(title="")
        text = paper2text(paper)
        self.assertNotIn("Title:", text)

    def test_paper_with_none_authors(self):
        """None authors should not crash."""
        paper = self._make_minimal_paper(authors=None)
        text = paper2text(paper)
        self.assertIsInstance(text, str)

    def test_paper_with_non_string_list_items(self):
        """Authors/categories lists with non-string items should not crash."""
        paper = self._make_minimal_paper(
            authors=[123, None, "Valid Author"],
            categories=[True, "cat1"],
        )
        text = paper2text(paper)
        self.assertIsInstance(text, str)
        self.assertIn("Valid Author", text)

    def test_paper_with_broken_extra(self):
        """Extra dict with unrepresentable objects should not crash."""
        paper = self._make_minimal_paper()
        object.__setattr__(paper, "extra", object())  # non-dict extra
        text = paper2text(paper)
        self.assertIsInstance(text, str)

    def test_paper2text_never_raises(self):
        """paper2text should NEVER raise an exception, no matter what."""
        # Test with a completely mangled object
        class FakePaper:
            pass

        fake = FakePaper()
        fake.source = None
        fake.paper_id = None
        fake.title = None
        fake.authors = None
        fake.abstract = None
        fake.published_date = None
        fake.url = None
        fake.doi = None
        fake.categories = None
        fake.keywords = None
        fake.citations = 0
        fake.references = None
        fake.extra = None
        fake.to_dict = lambda: {"paper_id": "fallback"}

        text = paper2text(fake)
        self.assertIsInstance(text, str)


class TestSourcePaperConstruction(unittest.TestCase):
    """Test that each source constructs valid Paper objects."""

    def _validate_paper(self, paper, source_name):
        """Validate a single Paper object has all required fields with correct types."""
        self.assertIsInstance(paper, Paper, f"[{source_name}] Should be Paper, got {type(paper)}")
        self.assertIsInstance(paper.paper_id, str, f"[{source_name}] paper_id should be str")
        self.assertIsInstance(paper.title, str, f"[{source_name}] title should be str")
        self.assertIsInstance(paper.authors, list, f"[{source_name}] authors should be list")
        self.assertIsInstance(paper.abstract, str, f"[{source_name}] abstract should be str")
        self.assertIsInstance(paper.doi, str, f"[{source_name}] doi should be str")
        self.assertIsInstance(paper.pdf_url, str, f"[{source_name}] pdf_url should be str")
        self.assertIsInstance(paper.url, str, f"[{source_name}] url should be str")
        self.assertIsInstance(paper.source, str, f"[{source_name}] source should be str")
        # published_date can be datetime or None
        if paper.published_date is not None:
            self.assertIsInstance(paper.published_date, datetime,
                                  f"[{source_name}] published_date should be datetime or None, got {type(paper.published_date)}")
        # to_dict should always work
        d = paper.to_dict()
        self.assertIsInstance(d, dict, f"[{source_name}] to_dict should return dict")
        # paper2text should always work
        text = paper2text(paper)
        self.assertIsInstance(text, str, f"[{source_name}] paper2text should return str")
        self.assertTrue(len(text) > 0, f"[{source_name}] paper2text should produce non-empty text")

    def test_arxiv_paper_construction(self):
        """ArxivSearcher constructs valid Papers."""
        from academic_mcp.sources.arxiv import ArxivSearcher
        searcher = ArxivSearcher()
        papers = searcher.search("machine learning", max_results=3)
        self.assertGreater(len(papers), 0, "ArXiv search should return results")
        for paper in papers:
            self._validate_paper(paper, "arxiv")
            self.assertEqual(paper.source, "arxiv")

    def test_pubmed_paper_construction(self):
        """PubMedSearcher constructs valid Papers."""
        from academic_mcp.sources.pubmed import PubMedSearcher
        searcher = PubMedSearcher()
        papers = searcher.search("cancer", max_results=3)
        self.assertGreater(len(papers), 0, "PubMed search should return results")
        for paper in papers:
            self._validate_paper(paper, "pubmed")
            self.assertEqual(paper.source, "pubmed")

    def test_pmc_paper_construction(self):
        """PMCSearcher constructs valid Papers."""
        from academic_mcp.sources.pmc import PMCSearcher
        searcher = PMCSearcher()
        papers = searcher.search("cancer treatment", max_results=3)
        self.assertGreater(len(papers), 0, "PMC search should return results")
        for paper in papers:
            self._validate_paper(paper, "pmc")
            self.assertEqual(paper.source, "pmc")

    def test_biorxiv_paper_construction(self):
        """BioRxivSearcher constructs valid Papers."""
        from academic_mcp.sources.biorxiv import BioRxivSearcher
        searcher = BioRxivSearcher()
        papers = searcher.search("cell biology", max_results=3, days=30)
        self.assertGreater(len(papers), 0, "bioRxiv search should return results")
        for paper in papers:
            self._validate_paper(paper, "biorxiv")
            self.assertEqual(paper.source, "biorxiv")
            self.assertTrue(paper.doi, "bioRxiv papers should have DOI")

    def test_medrxiv_paper_construction(self):
        """MedRxivSearcher constructs valid Papers."""
        from academic_mcp.sources.medrxiv import MedRxivSearcher
        searcher = MedRxivSearcher()
        papers = searcher.search("cardiovascular medicine", max_results=3, days=30)
        self.assertGreater(len(papers), 0, "medRxiv search should return results")
        for paper in papers:
            self._validate_paper(paper, "medrxiv")
            self.assertEqual(paper.source, "medrxiv")

    def test_crossref_paper_construction(self):
        """CrossRefSearcher constructs valid Papers."""
        from academic_mcp.sources.crossref import CrossRefSearcher
        searcher = CrossRefSearcher()
        papers = searcher.search("deep learning", max_results=3)
        if len(papers) == 0:
            self.skipTest("CrossRef returned no results (network/rate limit)")
        for paper in papers:
            self._validate_paper(paper, "crossref")
            self.assertEqual(paper.source, "crossref")
            self.assertTrue(paper.doi, "CrossRef papers should have DOI")

    def test_semantic_paper_construction(self):
        """SemanticSearcher constructs valid Papers."""
        from academic_mcp.sources.semantic import SemanticSearcher
        searcher = SemanticSearcher()
        papers = searcher.search("machine learning", max_results=3)
        if len(papers) == 0:
            self.skipTest("Semantic Scholar rate limited or no results")
        for paper in papers:
            self._validate_paper(paper, "semantic")
            self.assertEqual(paper.source, "semantic")

    def test_iacr_paper_construction(self):
        """IACRSearcher constructs valid Papers."""
        from academic_mcp.sources.iacr import IACRSearcher
        searcher = IACRSearcher()
        papers = searcher.search("cryptography", max_results=3, fetch_details=False)
        self.assertGreater(len(papers), 0, "IACR search should return results")
        for paper in papers:
            self._validate_paper(paper, "iacr")
            self.assertEqual(paper.source, "iacr")

    def test_google_scholar_paper_construction(self):
        """GoogleScholarSearcher constructs valid Papers (may fail due to blocking)."""
        from academic_mcp.sources.google_scholar import GoogleScholarSearcher
        searcher = GoogleScholarSearcher()
        try:
            papers = searcher.search("machine learning", max_results=3)
        except Exception:
            self.skipTest("Google Scholar blocked the request (expected)")
        if len(papers) == 0:
            self.skipTest("Google Scholar returned no results (likely blocked)")
        for paper in papers:
            self._validate_paper(paper, "google_scholar")
            self.assertEqual(paper.source, "google_scholar")

    def test_placeholder_sources_return_empty(self):
        """ACM, JSTOR, ResearchGate return empty lists (no API)."""
        from academic_mcp.sources.acm import ACMSearcher
        from academic_mcp.sources.jstor import JSTORSearcher
        from academic_mcp.sources.researchgate import ResearchGateSearcher

        for name, searcher in [
            ("acm", ACMSearcher()),
            ("jstor", JSTORSearcher()),
            ("researchgate", ResearchGateSearcher()),
        ]:
            papers = searcher.search("test", max_results=5)
            self.assertIsInstance(papers, list, f"{name} should return list")
            self.assertEqual(len(papers), 0, f"{name} should return empty list (no API)")


class TestMCPServerFormat(unittest.TestCase):
    """Test that the MCP server produces correctly formatted responses."""

    def test_async_search_per_query_returns_list(self):
        """async_search_per_query should always return a list."""
        import asyncio
        from academic_mcp.__main__ import PaperQuery, async_search_per_query

        async def run():
            query = PaperQuery(searcher="arxiv", query="machine learning", max_results=3)
            result = await async_search_per_query(query)
            self.assertIsInstance(result, list)
            if result:
                self.assertIsInstance(result[0], Paper)

        asyncio.run(run())

    def test_async_search_per_query_error_returns_empty_list(self):
        """async_search_per_query on error should return empty list, not raise."""
        import asyncio
        from academic_mcp.__main__ import PaperQuery, async_search_per_query

        async def run():
            # ACM has no public API - always returns empty list
            query = PaperQuery(searcher="acm", query="test", max_results=3)
            result = await async_search_per_query(query)
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 0, "ACM should return empty list (no public API)")

        asyncio.run(run())

    def test_paper_search_mcp_tool_returns_string(self):
        """MCP paper_search tool should return a string."""
        import asyncio
        from academic_mcp.__main__ import PaperQuery, paper_search

        async def run():
            query_list = [PaperQuery(searcher="arxiv", query="machine learning", max_results=3)]
            result = await paper_search(query_list)
            self.assertIsInstance(result, str, f"Expected str, got {type(result)}")
            self.assertTrue(len(result) > 0, "Result should be non-empty")

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()
