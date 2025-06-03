import logging
import os
from typing import Optional

try:
    from firecrawl import FirecrawlApp
except ImportError:
    # 如果没有安装 firecrawl-py，提供友好的错误信息
    FirecrawlApp = None

from src.config import FIRECRAWL_API_KEY

logger = logging.getLogger(__name__)


class FirecrawlClient:
    def __init__(self):
        if FirecrawlApp is None:
            raise ImportError(
                "firecrawl-py is not installed. Please install it with: pip install firecrawl-py"
            )
            
        api_key = FIRECRAWL_API_KEY
        if not api_key:
            logger.warning(
                "Firecrawl API key is not set. Please set FIRECRAWL_API_KEY environment variable. "
                "Get your API key at https://www.firecrawl.dev/app/usage"
            )
            raise ValueError("FIRECRAWL_API_KEY is required")
        
        self.app = FirecrawlApp(api_key=api_key)

    def crawl(self, url: str, return_format: str = "markdown") -> str:
        """
        爬取网页内容
        
        Args:
            url: 要爬取的网页URL
            return_format: 返回格式，支持 'markdown', 'html', 'text'
        
        Returns:
            爬取到的内容
        """
        try:
            # 使用 Firecrawl v1 API 的正确格式
            # 直接传递 formats 参数而不是嵌套在 params 中
            if return_format == "text":
                # Firecrawl 没有纯文本格式，使用 markdown
                formats = ['markdown']
            else:
                formats = [return_format]
            
            scrape_result = self.app.scrape_url(
                url,
                formats=formats
            )
            
            # Firecrawl v1 SDK 返回的是对象，不是字典
            # 需要访问 data 属性，然后从中获取内容
            if hasattr(scrape_result, 'data') and scrape_result.data:
                data = scrape_result.data
                if return_format == "markdown" or return_format == "text":
                    return data.get('markdown', '') if hasattr(data, 'get') else getattr(data, 'markdown', '')
                elif return_format == "html":
                    return data.get('html', '') if hasattr(data, 'get') else getattr(data, 'html', '')
                else:
                    return data.get('markdown', '') if hasattr(data, 'get') else getattr(data, 'markdown', '')
            else:
                # 如果没有 data 属性，尝试直接访问
                if return_format == "markdown" or return_format == "text":
                    return getattr(scrape_result, 'markdown', '')
                elif return_format == "html":
                    return getattr(scrape_result, 'html', '')
                else:
                    return getattr(scrape_result, 'markdown', '')
                
        except Exception as e:
            logger.error(f"Failed to crawl {url} with Firecrawl: {e}")
            return f"Error crawling {url}: {str(e)}"

    def extract_data(self, url: str, schema: dict) -> dict:
        """
        使用结构化数据提取功能
        
        Args:
            url: 要提取数据的网页URL
            schema: 数据结构定义
        
        Returns:
            提取的结构化数据
        """
        try:
            # 使用 v1 API 的 JSON 提取功能
            from firecrawl import JsonConfig
            
            json_config = JsonConfig(
                extractionSchema=schema,
                mode="llm-extraction"
            )
            
            extract_result = self.app.scrape_url(
                url,
                formats=["json"],
                json_options=json_config
            )
            
            # 处理响应对象
            if hasattr(extract_result, 'data') and extract_result.data:
                data = extract_result.data
                return data.get('json', {}) if hasattr(data, 'get') else getattr(data, 'json', {})
            else:
                return getattr(extract_result, 'json', {})
                
        except Exception as e:
            logger.error(f"Failed to extract data from {url}: {e}")
            return {}

    def batch_crawl(self, urls: list, return_format: str = "markdown") -> list:
        """
        批量爬取多个网页
        
        Args:
            urls: 要爬取的网页URL列表
            return_format: 返回格式
        
        Returns:
            爬取结果列表
        """
        results = []
        for url in urls:
            try:
                content = self.crawl(url, return_format)
                results.append({
                    'url': url,
                    'content': content,
                    'success': True
                })
            except Exception as e:
                results.append({
                    'url': url,
                    'content': f"Error: {str(e)}",
                    'success': False
                })
        return results 