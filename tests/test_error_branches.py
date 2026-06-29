"""
Tests that verify all try/except error handling branches are actually exercised.

These tests use mocks and broken objects to trigger every error path
added during the fix, ensuring exceptions don't propagate silently.
"""

import asyncio
import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

from academic_mcp.types import Paper, paper2text
from academic_mcp.__main__ import (
    PaperQuery,
    async_search_per_query,
    async_search_per_query_list,
    paper_search,
    engine2searcher,
)


# ═══════════════════════════════════════════════════════════════════════════════
# paper2text error branches
# ═══════════════════════════════════════════════════════════════════════════════

class TestPaper2TextExceptionBranches(unittest.TestCase):
    """Force every defensive branch in paper2text to execute."""

    def test_published_date_calls_strftime_exception_branch(self):
        """published_date is truthy but strftime fails → should use fallback."""
        paper = Paper(
            paper_id="p1", title="T", authors=["A"], abstract="", doi="",
            published_date=datetime(2024, 1, 1), pdf_url="", url="", source="test",
        )
        # Corrupt published_date to a non-datetime truthy value
        object.__setattr__(paper, "published_date", object())  # truthy, but no strftime
        text = paper2text(paper)
        self.assertIn("Published Date:", text)
        # The fallback should include the repr of the object
        self.assertNotIn("Error converting paper", text,
                         "Should not hit outer exception handler for this case")

    def test_authors_list_contains_non_string_types(self):
        """Authors with int/None/object entries should still render."""
        paper = Paper(
            paper_id="p1", title="T", authors=["OK", 123, None, object()],
            abstract="", doi="", published_date=datetime(2024, 1, 1),
            pdf_url="", url="", source="test",
        )
        text = paper2text(paper)
        self.assertIn("Authors:", text)
        self.assertIn("OK", text)
        self.assertIn("123", text)

    def test_to_dict_called_as_fallback_when_no_texts(self):
        """When all fields are falsy, to_dict fallback is used."""
        paper = Paper(
            paper_id="", title="", authors=[], abstract="", doi="",
            published_date=None, pdf_url="", url="", source="",
        )
        text = paper2text(paper)
        self.assertIn("paper_id", text)  # from to_dict fallback

    def test_outer_exception_handler_triggers_on_complete_garbage(self):
        """When paper.to_dict() itself fails, outermost except fires."""
        class TotallyBrokenPaper:
            # All fields are falsy → no texts collected → to_dict() called → raises
            source = ""
            paper_id = ""
            title = ""
            authors = []
            abstract = ""
            published_date = None
            url = ""
            doi = ""
            categories = None
            keywords = None
            citations = 0
            references = None
            extra = None

            def to_dict(self):
                raise RuntimeError("SIMULATED to_dict CRASH")

        text = paper2text(TotallyBrokenPaper())
        self.assertIsInstance(text, str)
        self.assertIn("Error converting paper to text", text)
        self.assertIn("SIMULATED to_dict CRASH", text)


# ═══════════════════════════════════════════════════════════════════════════════
# async_search_per_query error branches
# ═══════════════════════════════════════════════════════════════════════════════

class TestAsyncSearchPerQueryExceptionBranches(unittest.TestCase):
    """Force exception paths in async_search_per_query."""

    def test_searcher_search_raises_exception_returns_empty_list(self):
        """If searcher.search() raises, we catch it and return []."""

        async def run():
            from academic_mcp.sources.arxiv import ArxivSearcher
            # Mock the search method to raise
            with patch.object(ArxivSearcher, 'search', side_effect=ConnectionError("SIMULATED NETWORK FAILURE")):
                query = PaperQuery(searcher="arxiv", query="test", max_results=3)
                result = await async_search_per_query(query)
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 0, "Should return empty list on exception, not raise")

        asyncio.run(run())

    def test_searcher_not_in_engine2searcher_returns_empty(self):
        """When searcher is missing from engine2searcher at call time, log warning + return []."""
        # Create query first (passes validation while arxiv is still registered)
        query = PaperQuery(searcher="arxiv", query="test", max_results=3)

        async def run():
            # Simulate searcher removed by patching the dict lookup
            with patch('academic_mcp.__main__.engine2searcher', {}):
                result = await async_search_per_query(query)
                self.assertEqual(len(result), 0)

        asyncio.run(run())


# ═══════════════════════════════════════════════════════════════════════════════
# async_search_per_query_list error branches
# ═══════════════════════════════════════════════════════════════════════════════

class TestAsyncSearchPerQueryListExceptionBranches(unittest.TestCase):
    """Force exception paths with return_exceptions=True."""

    def test_one_query_fails_other_succeeds(self):
        """When one query raises Exception, the other still returns results."""

        async def broken_search(query):
            if query.searcher == "bad_source":
                raise RuntimeError("SIMULATED SEARCHER CRASH")
            # Simulate normal arxiv behavior
            return [Paper(
                paper_id="test123", title="Test Paper", authors=["Author"],
                abstract="Abstract", doi="", published_date=datetime(2024, 1, 1),
                pdf_url="", url="", source="arxiv",
            )]

        saved = {}
        try:
            from academic_mcp.__main__ import async_search_per_query as original
            import academic_mcp.__main__ as main_mod
            saved['func'] = main_mod.async_search_per_query
            main_mod.async_search_per_query = broken_search

            # Create queries: one bad, one good
            q_good = PaperQuery(searcher="arxiv", query="test", max_results=3)

            # We need a bad searcher that passes validation
            # Use ACM (returns empty) but mock it to raise
            import academic_mcp.__main__ as mm
            mm.engine2searcher["bad_source"] = mm.engine2searcher.get("arxiv")

            q_bad = PaperQuery(searcher="bad_source", query="test", max_results=3)

            async def run():
                result = await async_search_per_query_list([q_good, q_bad])
                return result

            papers = asyncio.run(run())
            # The good query should still produce results
            self.assertGreater(len(papers), 0, "Good query results should survive bad query failure")
            self.assertTrue(any(p.source == "arxiv" for p in papers))

        finally:
            import academic_mcp.__main__ as mm
            mm.async_search_per_query = saved.get('func', mm.async_search_per_query)
            mm.engine2searcher.pop("bad_source", None)


# ═══════════════════════════════════════════════════════════════════════════════
# paper_search top-level error branches
# ═══════════════════════════════════════════════════════════════════════════════

class TestPaperSearchExceptionBranches(unittest.TestCase):
    """Force the top-level try/except in paper_search."""

    def test_xmap_async_failure_returns_error_string(self):
        """When xmap_async itself raises, we return an error string, not crash."""

        async def run():
            with patch('academic_mcp.__main__.xmap_async', side_effect=RuntimeError("SIMULATED XMAP CRASH")):
                result = await paper_search([
                    PaperQuery(searcher="arxiv", query="test", max_results=3)
                ])
            self.assertIsInstance(result, str)
            self.assertIn("Search failed", result)
            self.assertIn("SIMULATED XMAP CRASH", result)

        asyncio.run(run())

    def test_paper2text_failure_skips_bad_paper(self):
        """When paper2text raises for one paper, others still render."""

        async def run():
            with patch('academic_mcp.__main__.paper2text', side_effect=[
                "Paper 1 text OK",            # first paper succeeds
                RuntimeError("SIMULATED TEXT CONVERSION FAILURE"),  # second fails
                "Paper 3 text OK",            # third succeeds
            ]):
                # Mock xmap_async to return 3 fake papers
                with patch('academic_mcp.__main__.xmap_async', return_value=[
                    Paper(paper_id="p1", title="OK1", authors=[], abstract="", doi="",
                          published_date=datetime(2024, 1, 1), pdf_url="", url="", source="arxiv"),
                    Paper(paper_id="p2", title="BAD", authors=[], abstract="", doi="",
                          published_date=datetime(2024, 1, 1), pdf_url="", url="", source="arxiv"),
                    Paper(paper_id="p3", title="OK3", authors=[], abstract="", doi="",
                          published_date=datetime(2024, 1, 1), pdf_url="", url="", source="arxiv"),
                ]):
                    result = await paper_search([
                        PaperQuery(searcher="arxiv", query="test", max_results=3)
                    ])
            self.assertIsInstance(result, str)
            self.assertIn("Paper 1 text OK", result)
            self.assertNotIn("SIMULATED TEXT CONVERSION FAILURE", result,
                             "Failed paper should be skipped, not crash the output")
            self.assertIn("Paper 3 text OK", result)

        asyncio.run(run())

    def test_paper_is_dict_error_skipped(self):
        """Papers returned as {"error": ...} dict should be logged and skipped."""

        async def run():
            with patch('academic_mcp.__main__.xmap_async', return_value=[
                Paper(paper_id="p1", title="OK", authors=[], abstract="", doi="",
                      published_date=datetime(2024, 1, 1), pdf_url="", url="", source="arxiv"),
                {"error": "rate_limited", "message": "SIMULATED API LIMIT"},
                Paper(paper_id="p3", title="OK3", authors=[], abstract="", doi="",
                      published_date=datetime(2024, 1, 1), pdf_url="", url="", source="arxiv"),
            ]):
                result = await paper_search([
                    PaperQuery(searcher="arxiv", query="test", max_results=3)
                ])
            self.assertIsInstance(result, str)
            self.assertIn("OK", result)
            self.assertIn("OK3", result)
            # The dict error should not appear in output
            self.assertNotIn("rate_limited", result)

        asyncio.run(run())

    def test_paper_is_none_skipped(self):
        """None papers in the result should be skipped."""
        async def run():
            with patch('academic_mcp.__main__.xmap_async', return_value=[
                Paper(paper_id="p1", title="OK", authors=[], abstract="", doi="",
                      published_date=datetime(2024, 1, 1), pdf_url="", url="", source="arxiv"),
                None,
                Paper(paper_id="p3", title="OK3", authors=[], abstract="", doi="",
                      published_date=datetime(2024, 1, 1), pdf_url="", url="", source="arxiv"),
            ]):
                result = await paper_search([
                    PaperQuery(searcher="arxiv", query="test", max_results=3)
                ])
            self.assertIsInstance(result, str)
            self.assertIn("OK", result)
            self.assertIn("OK3", result)

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()
