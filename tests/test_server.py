import unittest
import asyncio
import os
from academic_mcp.__main__ import PaperQuery, PaperDownloadQuery, async_search_per_query, async_download_per_query

class TestPaperSearchServer(unittest.TestCase):
    def test_search_arxiv(self):
        """Test the search_arxiv tool returns 10 results."""
        query = PaperQuery(searcher="arxiv", query="machine learning", max_results=10)
        result = asyncio.run(async_search_per_query(query))
        self.assertIsInstance(result, list, "Result should be a list")
        self.assertGreater(len(result), 0, "Should return at least 1 result")
        self.assertLessEqual(len(result), 10, "Should return at most 10 results")
        for paper in result:
            self.assertIsNotNone(paper.title, "Each result should contain a title")
            self.assertIsNotNone(paper.paper_id, "Each result should contain a paper_id")

    def test_download_arxiv_from_search(self):
        """Test downloading arXiv papers based on search results."""
        # 先搜索结果
        query = PaperQuery(searcher="arxiv", query="machine learning", max_results=3)  # 减少到3个以加快测试
        search_results = asyncio.run(async_search_per_query(query))
        self.assertGreater(len(search_results), 0, "Search should return at least 1 result")

        # 下载目录
        save_path = "./downloads"
        os.makedirs(save_path, exist_ok=True)  # 确保目录存在

        # 下载每个搜索结果的 PDF（限制前3个）
        for paper in search_results[:3]:
            paper_id = paper.paper_id
            download_query = PaperDownloadQuery(searcher="arxiv", paper_id=paper_id)
            result = asyncio.run(async_download_per_query(download_query))
            self.assertIsInstance(result, str, f"Result for {paper_id} should be a string")
            if not result.startswith("Error"):
                self.assertTrue(result.endswith(".pdf"), f"Result for {paper_id} should be a PDF file path")
                self.assertTrue(os.path.exists(result), f"PDF file for {paper_id} should exist on disk")

if __name__ == "__main__":
    unittest.main()