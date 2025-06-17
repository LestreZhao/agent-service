import logging
import re
from typing import Optional
from src.agents.llm import get_llm_by_provider
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)

class TitleGenerator:
    """智能标题生成器，根据内容生成合适的中文标题"""
    
    def __init__(self):
        self.llm = get_llm_by_provider("openai")  # 使用OpenAI生成标题
    
    def generate_chinese_title(self, content: str, agent_name: str, max_length: int = 50) -> str:
        """
        根据内容生成中文标题
        
        Args:
            content: 文档内容
            agent_name: 智能体名称
            max_length: 标题最大长度
            
        Returns:
            生成的中文标题
        """
        try:
            # 截取内容前1000字符进行分析
            content_preview = content[:1000] if len(content) > 1000 else content
            
            prompt = f"""
请根据以下内容为文档生成一个简洁、准确的中文标题。

智能体类型：{agent_name}
文档内容预览：
{content_preview}

要求：
1. 标题必须是中文
2. 长度控制在{max_length}个字符以内
3. 准确反映文档的核心内容和主题
4. 简洁明了，易于理解
5. 不包含特殊字符（如/、\、:、*、?、"、<、>、|）
6. 根据智能体类型和内容特点生成对应的标题

智能体类型说明：
- researcher: 研究分析类内容
- coder: 代码开发类内容

- db_analyst: 数据库分析类内容
- document_parser: 文档解析类内容
- reporter: 综合报告类内容
- chart_generator: 图表生成类内容

只返回标题，不要其他说明文字。
"""
            
            logger.debug(f"正在为{agent_name}生成标题，内容长度: {len(content)}")
            
            # 调用LLM生成标题
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            
            # 提取并清理标题
            title = self._clean_title(response.content, max_length)
            
            logger.info(f"为{agent_name}生成标题: {title}")
            return title
            
        except Exception as e:
            logger.error(f"生成标题失败: {e}")
            # 返回默认标题
            return self._generate_fallback_title(agent_name)
    
    def _clean_title(self, raw_title: str, max_length: int) -> str:
        """清理和格式化标题"""
        if not raw_title:
            return "未知内容"
        
        # 移除前后空格和换行符
        title = raw_title.strip()
        
        # 移除可能的引号
        title = title.strip('"\'"""''')
        
        # 移除文件系统不支持的字符
        forbidden_chars = r'[/\\:*?"<>|]'
        title = re.sub(forbidden_chars, '', title)
        
        # 移除多余的空格
        title = re.sub(r'\s+', ' ', title)
        
        # 限制长度
        if len(title) > max_length:
            title = title[:max_length-3] + "..."
        
        # 如果标题为空，返回默认值
        if not title.strip():
            return "文档总结"
        
        return title.strip()
    
    def _generate_fallback_title(self, agent_name: str) -> str:
        """生成后备标题"""
        fallback_titles = {
            "researcher": "研究分析报告",
            "coder": "代码开发总结",

            "db_analyst": "数据库分析结果",
            "document_parser": "文档解析报告",
            "reporter": "综合分析报告",
            "chart_generator": "图表生成结果"
        }
        
        return fallback_titles.get(agent_name, f"{agent_name}执行结果")

# 创建全局实例
title_generator = TitleGenerator() 