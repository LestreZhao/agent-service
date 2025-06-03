#!/usr/bin/env python3
"""
调试原始的 SSE 流
"""

import requests

def debug_raw_stream():
    """查看原始的 SSE 流"""
    
    # 测试消息
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "分析苹果公司股价"
            }
        ],
        "debug": True
    }
    
    print("发送请求到 /api/chat/stream...\n")
    
    # 发送请求
    response = requests.post(
        'http://localhost:8000/api/chat/stream',
        json=payload,
        stream=True,
        headers={'Accept': 'text/event-stream'}
    )
    
    print("原始 SSE 流内容：")
    print("="*50)
    
    line_count = 0
    for line in response.iter_lines():
        line_count += 1
        if line:
            decoded_line = line.decode('utf-8')
            print(f"行 {line_count}: {decoded_line}")
            
            # 特别标记我们关心的事件
            if "plan_generated" in decoded_line:
                print("  ^^^ 发现 plan_generated 事件！")
            elif "step_started" in decoded_line:
                print("  ^^^ 发现 step_started 事件！")
            elif "step_end" in decoded_line:
                print("  ^^^ 发现 step_end 事件！")
        else:
            print(f"行 {line_count}: [空行]")
        
        # 限制输出行数，避免太长
        if line_count > 200:
            print("\n... (输出被截断，已显示前 200 行)")
            break
    
    print("\n" + "="*50)
    print(f"总共接收到 {line_count} 行")

if __name__ == "__main__":
    debug_raw_stream() 