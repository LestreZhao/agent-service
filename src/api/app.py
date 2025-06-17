"""
FastAPI application for FusionAI.

This module defines the FastAPI application for the FusionAI LangGraph-based agent workflow.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse
import asyncio
from typing import AsyncGenerator, Dict, List, Any

from src.graph import build_graph
from src.config import TEAM_MEMBERS
from src.service.workflow_service import run_agent_workflow
from .document_routes import router as document_router

# Configure logging
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="FusionAI API",
    description="API for FusionAI LangGraph-based agent workflow with document processing capabilities",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include document router
app.include_router(document_router, prefix="/api")

# Create the graph
graph = build_graph()


class ContentItem(BaseModel):
    type: str = Field(..., description="The type of content (text, image, etc.)")
    text: Optional[str] = Field(None, description="The text content if type is 'text'")
    image_url: Optional[str] = Field(
        None, description="The image URL if type is 'image'"
    )


class ChatMessage(BaseModel):
    role: str = Field(
        ..., description="The role of the message sender (user or assistant)"
    )
    content: Union[str, List[ContentItem]] = Field(
        ...,
        description="The content of the message, either a string or a list of content items",
    )


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="The conversation history")
    debug: Optional[bool] = Field(False, description="Whether to enable debug logging")
    deep_thinking_mode: Optional[bool] = Field(
        False, description="Whether to enable deep thinking mode"
    )
    search_before_planning: Optional[bool] = Field(
        False, description="Whether to search before planning"
    )


@app.post("/api/chat/stream")
async def chat_endpoint(request: ChatRequest, req: Request):
    """
    Chat endpoint for LangGraph invoke.

    Args:
        request: The chat request
        req: The FastAPI request object for connection state checking

    Returns:
        The streamed response
    """
    try:
        # Convert Pydantic models to dictionaries and normalize content format
        messages = []
        for msg in request.messages:
            message_dict = {"role": msg.role}

            # Handle both string content and list of content items
            if isinstance(msg.content, str):
                message_dict["content"] = msg.content
            else:
                # For content as a list, convert to the format expected by the workflow
                content_items = []
                for item in msg.content:
                    if item.type == "text" and item.text:
                        content_items.append({"type": "text", "text": item.text})
                    elif item.type == "image" and item.image_url:
                        content_items.append(
                            {"type": "image", "image_url": item.image_url}
                        )

                message_dict["content"] = content_items

            messages.append(message_dict)

        async def event_generator():
            try:
                async for event in run_agent_workflow(
                    messages,
                    request.debug,
                    request.deep_thinking_mode,
                    request.search_before_planning,
                ):
                    # Check if client is still connected
                    if await req.is_disconnected():
                        logger.info("Client disconnected, stopping workflow")
                        break
                    yield {
                        "event": event["event"],
                        "data": json.dumps(event["data"], ensure_ascii=False),
                    }
            except asyncio.CancelledError:
                logger.info("Stream processing cancelled")
                raise

        return EventSourceResponse(
            event_generator(),
            media_type="text/event-stream",
            sep="\n",
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/config/agents")
async def get_agent_configuration():
    """
    获取智能体配置信息
    
    Returns:
        智能体和LLM配置的详细信息
    """
    try:
        from src.utils.startup_info import startup_display
        from src.agents.llm import list_supported_providers
        
        # 获取配置信息
        agent_mapping = startup_display.get_agent_model_mapping()
        llm_usage = startup_display.get_llm_usage_summary()
        
        # 构建详细的配置信息
        agent_details = []
        for agent_name, agent_info in startup_display.agent_info.items():
            agent_details.append({
                "name": agent_name,
                "description": agent_info["description"],
                "llm_type": agent_info["llm_type"],
                "model": agent_info["model"],
                "provider": agent_info["provider"],
                "is_team_member": agent_info["is_team_member"]
            })
        
        # LLM配置信息
        llm_configs = []
        for llm_type, config in startup_display.llm_configs.items():
            llm_configs.append({
                "type": llm_type,
                "model": config["model"],
                "provider": config["provider"],
                "base_url": config["base_url"],
                "api_key_configured": config["api_key_configured"]
            })
        
        # 获取支持的厂商信息
        supported_providers = list_supported_providers()
        
        return {
            "success": True,
            "data": {
                "agents": agent_details,
                "llm_configs": llm_configs,
                "supported_providers": supported_providers,
                "team_members": list(TEAM_MEMBERS),
                "usage_statistics": llm_usage,
                "total_agents": len(agent_details)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting agent configuration: {e}")
        raise HTTPException(status_code=500, detail=f"获取配置信息失败: {str(e)}")


@app.get("/api/config/providers")
async def get_supported_providers():
    """
    获取支持的LLM厂商信息
    
    Returns:
        支持的厂商详细信息
    """
    try:
        from src.agents.llm import list_supported_providers, detect_provider_by_model
        
        providers = list_supported_providers()
        
        # 添加一些示例模型的检测结果
        example_models = [
            "gpt-4o", "claude-3-5-sonnet-20241022", "gemini-2.5-pro-preview-06-05",
            "qwen2-7b-instruct", "deepseek-chat", "llama3.1:8b"
        ]
        
        model_detection_examples = []
        for model in example_models:
            provider = detect_provider_by_model(model)
            model_detection_examples.append({
                "model": model,
                "detected_provider": provider
            })
        
        return {
            "success": True,
            "data": {
                "providers": providers,
                "model_detection_examples": model_detection_examples,
                "total_providers": len(providers)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting provider information: {e}")
        raise HTTPException(status_code=500, detail=f"获取厂商信息失败: {str(e)}")
