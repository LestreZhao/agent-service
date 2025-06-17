import logging
import os
from typing import Dict, Any
from src.config.agents import AGENT_LLM_MAP, LLMProvider
from src.config import TEAM_MEMBERS

logger = logging.getLogger(__name__)

class StartupInfoDisplay:
    """启动时显示智能体和LLM配置信息"""
    
    def __init__(self):
        self.provider_configs = self._get_provider_configs()
        self.agent_info = self._get_agent_info()
    
    def _get_provider_configs(self) -> Dict[LLMProvider, Dict[str, Any]]:
        """获取所有厂商的配置信息"""
        try:
            from src.agents.llm import list_supported_providers
            return list_supported_providers()
        except ImportError:
            # 回退到基础配置
            return {
                "openai": {"model": "gpt-4o", "api_key_configured": False},
                "deepseek": {"model": "deepseek-chat", "api_key_configured": False},
                "google": {"model": "gemini-2.5-pro-preview-06-05", "api_key_configured": False},
            }
    
    def _get_agent_info(self) -> Dict[str, Dict[str, str]]:
        """获取智能体信息"""
        agent_descriptions = {
            "coordinator": "任务协调员 - 负责接收用户任务并协调整个工作流程",
            "planner": "任务规划员 - 负责分解复杂任务并制定执行计划",
            "supervisor": "任务监督员 - 负责监督任务执行过程并做出决策",
            "researcher": "研究员 - 负责网络搜索和信息收集",
            "coder": "程序员 - 负责代码编写和数据处理",
            "reporter": "报告员 - 负责整理结果并生成最终报告",
            "db_analyst": "数据库分析师 - 负责数据库查询和数据分析",
            "document_parser": "文档解析员 - 负责文档解析和内容提取",
            "chart_generator": "图表生成员 - 负责数据可视化和图表生成"
        }
        
        agent_info = {}
        for agent_name, provider in AGENT_LLM_MAP.items():
            provider_config = self.provider_configs.get(provider, {})
            agent_info[agent_name] = {
                "description": agent_descriptions.get(agent_name, f"{agent_name} - 专用智能体"),
                "provider": provider,
                "model": provider_config.get("model", "未配置"),
                "provider_display": self._get_provider_display_name(provider),
                "is_team_member": agent_name in TEAM_MEMBERS
            }
        
        return agent_info
    
    def _get_provider_display_name(self, provider: str) -> str:
        """获取厂商显示名称"""
        provider_name_map = {
            "openai": "OpenAI",
            "claude": "Anthropic Claude",
            "google": "Google Gemini",
            "qwen": "阿里通义千问",
            "deepseek": "DeepSeek",
            "ollama": "Ollama"
        }
        return provider_name_map.get(provider, provider.title())
    
    def display_startup_info(self):
        """显示启动配置信息"""
        logger.info("="*80)
        logger.info("🚀 FusionAI 智能体系统启动配置信息")
        logger.info("="*80)
        
        # 显示支持的厂商信息
        self._display_supported_providers()
        
        # 显示厂商配置
        self._display_provider_configs()
        
        # 显示智能体配置
        self._display_agent_configs()
        
        # 显示工作流团队成员
        self._display_team_members()
        
        logger.info("="*80)
    
    def _display_supported_providers(self):
        """显示支持的厂商信息"""
        try:
            from src.agents.llm import list_supported_providers
            providers = list_supported_providers()
            
            logger.info("\n🏭 支持的LLM厂商:")
            logger.info("-" * 50)
            
            for provider, info in providers.items():
                display_name = self._get_provider_display_name(provider)
                logger.info(f"  {provider:<10} | {display_name:<20} | {info['llm_class']:<25}")
            
        except ImportError:
            logger.info("\n🏭 厂商信息: 无法加载详细厂商信息")
    
    def _display_provider_configs(self):
        """显示厂商配置信息"""
        logger.info("\n📋 厂商模型配置:")
        logger.info("-" * 50)
        
        for provider, config in self.provider_configs.items():
            status = "✅" if config.get("api_key_configured", False) else "❌"
            display_name = self._get_provider_display_name(provider)
            model = config.get("model", "未配置")
            logger.info(f"{provider.upper():>10} | {display_name:<20} | {model:<25} | {status}")
            
            base_url = config.get("base_url")
            if base_url:
                logger.info(f"{'':>12} | Base URL: {base_url}")
        
        logger.info("")
    
    def _display_agent_configs(self):
        """显示智能体配置信息"""
        logger.info("🤖 智能体配置:")
        logger.info("-" * 50)
        
        # 按厂商分组显示
        provider_groups = {}
        for agent_name, agent_info in self.agent_info.items():
            provider = agent_info["provider"]
            if provider not in provider_groups:
                provider_groups[provider] = []
            provider_groups[provider].append((agent_name, agent_info))
        
        for provider, agents in provider_groups.items():
            display_name = self._get_provider_display_name(provider)
            logger.info(f"\n{display_name} 厂商智能体:")
            for agent_name, agent_info in agents:
                team_mark = "👥" if agent_info["is_team_member"] else "🔧"
                logger.info(f"  {team_mark} {agent_name:<15} | {agent_info['model']:<25} | {agent_info['description']}")
    
    def _display_team_members(self):
        """显示工作流团队成员"""
        logger.info(f"\n👥 工作流团队成员 ({len(TEAM_MEMBERS)} 个):")
        logger.info("-" * 50)
        
        for member in TEAM_MEMBERS:
            if member in self.agent_info:
                info = self.agent_info[member]
                logger.info(f"  • {member:<15} | {info['provider']:<10} | {info['model']}")
    
    def get_agent_model_mapping(self) -> Dict[str, str]:
        """获取智能体到模型的映射关系"""
        return {
            agent_name: info["model"] 
            for agent_name, info in self.agent_info.items()
        }
    
    def get_provider_usage_summary(self) -> Dict[str, int]:
        """获取厂商使用统计"""
        usage = {}
        for info in self.agent_info.values():
            provider = info["provider"]
            usage[provider] = usage.get(provider, 0) + 1
        return usage

# 创建全局实例
startup_display = StartupInfoDisplay() 