from langgraph.prebuilt import create_react_agent

from src.prompts import apply_prompt_template
from src.tools import (
    bash_tool,
    browser_tool,
    crawl_tool,
    python_repl_tool,
    tavily_tool,
    oracle_table_info_tool,
    oracle_query_tool,
    oracle_relationships_tool,
    document_analysis_tool,
)
from src.tools.file_info_tool import task_files_json_tool

from .llm import get_llm_by_type
from src.config.agents import AGENT_LLM_MAP

# Create agents using configured LLM types
research_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["researcher"]),
    tools=[tavily_tool, crawl_tool],
    prompt=lambda state: apply_prompt_template("researcher", state),
)

coder_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["coder"]),
    tools=[python_repl_tool, bash_tool],
    prompt=lambda state: apply_prompt_template("coder", state),
)

browser_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["browser"]),
    tools=[browser_tool],
    prompt=lambda state: apply_prompt_template("browser", state),
)

db_analyst_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["db_analyst"]),
    tools=[oracle_table_info_tool, oracle_query_tool, oracle_relationships_tool],
    prompt=lambda state: apply_prompt_template("db_analyst", state),
)

document_parser_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["document_parser"]),
    tools=[document_analysis_tool],
    prompt=lambda state: apply_prompt_template("document_parser", state),
)

reporter_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["reporter"]),
    tools=[task_files_json_tool],
    prompt=lambda state: apply_prompt_template("reporter", state),
)
