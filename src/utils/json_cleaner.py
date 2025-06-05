import re


def clean_json_response(response: str) -> str:
    """
    清理LLM返回的JSON格式，移除markdown代码块标记
    
    Args:
        response: LLM返回的原始响应内容
        
    Returns:
        清理后的JSON字符串
    """
    # 移除开头和结尾的空白字符
    cleaned = response.strip()
    
    # 使用正则表达式匹配和移除markdown代码块
    # 匹配 ```语言标识符 开头和 ``` 结尾的整个代码块
    code_block_pattern = r'^```(?:\w+\s*)?\n?(.*?)\n?```$'
    match = re.match(code_block_pattern, cleaned, re.DOTALL)
    
    if match:
        # 如果匹配到代码块格式，提取内容
        cleaned = match.group(1).strip()
    else:
        # 如果没有匹配到完整代码块，尝试简单的前缀/后缀移除
        # 处理开头的```json标记（可能有换行）
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:].strip()
        elif cleaned.startswith("```"):
            # 移除```及后面可能的语言标识符到第一个换行符
            first_newline = cleaned.find('\n')
            if first_newline != -1:
                cleaned = cleaned[first_newline + 1:].strip()
            else:
                cleaned = cleaned[3:].strip()
        
        # 处理结尾的```标记
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
    
    return cleaned.strip() 