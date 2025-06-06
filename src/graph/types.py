from typing import Literal, Union
from typing_extensions import TypedDict
from langgraph.graph import MessagesState

from src.config import TEAM_MEMBERS

# Define routing options
OPTIONS = TEAM_MEMBERS + ["FINISH"]

# 创建动态的 Literal 类型
RouterNext = Union[
    Literal["researcher"],
    Literal["coder"], 
    Literal["reporter"],
    Literal["db_analyst"],
    Literal["document_parser"],
    Literal["chart_generator"],
    Literal["FINISH"]
]


class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""

    next: RouterNext


class State(MessagesState):
    """State for the agent system, extends MessagesState with next field."""

    # Constants
    TEAM_MEMBERS: list[str]

    # Runtime Variables
    next: str
    full_plan: str
    deep_thinking_mode: bool
    search_before_planning: bool
    
    # 新增字段：执行总结追踪
    execution_summaries: list[dict]  # 使用通用dict类型避免循环导入
    output_directory: str
    task_id: str
