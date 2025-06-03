import sys

from .article import Article
from .firecrawl_client import FirecrawlClient
from .readability_extractor import ReadabilityExtractor


class Crawler:
    def crawl(self, url: str) -> Article:
        # 使用 Firecrawl 获取更高质量的网页内容
        # Firecrawl 提供了更好的内容提取和清理功能
        # 支持直接输出 Markdown 格式，减少后处理步骤
        
        try:
            firecrawl_client = FirecrawlClient()
            # 直接获取 Markdown 格式的内容，Firecrawl 的内容质量通常很好
            markdown_content = firecrawl_client.crawl(url, return_format="markdown")
            
            # 创建 Article 对象
            title = self._extract_title_from_markdown(markdown_content)
            # 对于 Firecrawl 的 markdown 内容，我们将其转换为 HTML 以保持兼容性
            html_content = f"<html><body>{markdown_content}</body></html>"
            article = Article(title=title, html_content=html_content)
            article.url = url
            article.content = markdown_content  # 保存原始 markdown 内容
            
            return article
            
        except Exception as e:
            # 如果 Firecrawl 失败，回退到 HTML + readability 方案
            print(f"Firecrawl failed: {e}, falling back to HTML + readability extraction")
            
            try:
                firecrawl_client = FirecrawlClient()
                html = firecrawl_client.crawl(url, return_format="html")
                extractor = ReadabilityExtractor()
                article = extractor.extract_article(html)
                article.url = url
                return article
            except Exception as fallback_error:
                # 最终回退：返回错误信息
                error_content = f"Failed to extract content from {url}. Error: {str(fallback_error)}"
                article = Article(title="Error extracting content", html_content=f"<p>{error_content}</p>")
                article.url = url
                return article

    def _extract_title_from_markdown(self, markdown_content: str) -> str:
        """从 Markdown 内容中提取标题"""
        lines = markdown_content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
        
        # 如果没有找到 H1 标题，尝试找 H2
        for line in lines:
            line = line.strip()
            if line.startswith('## '):
                return line[3:].strip()
        
        return "Untitled"

    def extract_structured_data(self, url: str, schema: dict) -> dict:
        """
        使用 Firecrawl 的结构化数据提取功能
        
        Args:
            url: 要提取数据的网页URL  
            schema: 数据结构定义
        
        Returns:
            提取的结构化数据
        """
        try:
            firecrawl_client = FirecrawlClient()
            return firecrawl_client.extract_data(url, schema)
        except Exception as e:
            print(f"Failed to extract structured data: {e}")
            return {}


if __name__ == "__main__":
    if len(sys.argv) == 2:
        url = sys.argv[1]
    else:
        url = "https://fintel.io/zh-hant/s/br/nvdc34"
    crawler = Crawler()
    article = crawler.crawl(url)
    print(article.to_markdown())
