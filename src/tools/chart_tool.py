from langchain.tools import Tool
from typing import Dict, List, Any, Optional
import json
import re
from datetime import datetime


def generate_echarts_chart(data_input: str, chart_type: str = "auto", chart_title: str = "", analysis_requirements: str = "") -> str:
    """
    生成ECharts图表JSON配置
    
    Args:
        data_input: 数据输入，可以是JSON字符串、CSV格式或描述性文本
        chart_type: 图表类型 (auto, line, bar, pie, scatter, radar, funnel, gauge, heatmap)
        chart_title: 图表标题
        analysis_requirements: 分析要求和图表需求描述
        
    Returns:
        ECharts图表配置的JSON字符串
    """
    try:
        # 解析数据输入
        parsed_data = parse_data_input(data_input)
        
        if not parsed_data:
            return json.dumps({
                "error": "无法解析输入数据",
                "success": False,
                "input_received": data_input
            }, ensure_ascii=False)
        
        # 智能选择图表类型
        if chart_type == "auto":
            chart_type = auto_select_chart_type(parsed_data, analysis_requirements)
        
        # 生成图表配置
        chart_config = generate_chart_config(
            data=parsed_data,
            chart_type=chart_type,
            title=chart_title,
            requirements=analysis_requirements
        )
        
        return json.dumps({
            "success": True,
            "chart_type": chart_type,
            "chart_config": chart_config,
            "data_summary": {
                "records_count": len(parsed_data.get("data", [])),
                "columns": list(parsed_data.get("columns", {}).keys()),
                "chart_title": chart_title
            }
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"生成图表失败: {str(e)}",
            "success": False,
            "input_received": data_input
        }, ensure_ascii=False)


def parse_data_input(data_input: str) -> Dict[str, Any]:
    """解析各种格式的数据输入"""
    try:
        # 尝试解析JSON格式
        if data_input.strip().startswith('{') or data_input.strip().startswith('['):
            data = json.loads(data_input)
            return normalize_json_data(data)
        
        # 尝试解析CSV格式
        elif ',' in data_input and '\n' in data_input:
            return parse_csv_data(data_input)
        
        # 尝试解析表格格式
        elif '|' in data_input:
            return parse_table_data(data_input)
        
        # 描述性数据
        else:
            return parse_descriptive_data(data_input)
            
    except Exception as e:
        return {"error": f"数据解析失败: {str(e)}"}


def normalize_json_data(data: Any) -> Dict[str, Any]:
    """标准化JSON数据格式"""
    if isinstance(data, list):
        if not data:
            return {"data": [], "columns": {}}
        
        # 如果是对象数组
        if isinstance(data[0], dict):
            columns = {}
            for key in data[0].keys():
                # 判断数据类型
                sample_value = data[0][key]
                if isinstance(sample_value, (int, float)):
                    columns[key] = "number"
                elif isinstance(sample_value, str):
                    try:
                        float(sample_value)
                        columns[key] = "number"
                    except:
                        columns[key] = "string"
                else:
                    columns[key] = "string"
            
            return {"data": data, "columns": columns}
        
        # 如果是简单数组
        else:
            return {
                "data": [{"value": item, "index": i} for i, item in enumerate(data)],
                "columns": {"value": "number" if isinstance(data[0], (int, float)) else "string", "index": "number"}
            }
    
    elif isinstance(data, dict):
        # 如果直接是数据对象
        return {"data": [data], "columns": {key: "string" for key in data.keys()}}
    
    return {"data": [], "columns": {}}


def parse_csv_data(csv_text: str) -> Dict[str, Any]:
    """解析CSV格式数据"""
    lines = csv_text.strip().split('\n')
    if len(lines) < 2:
        return {"data": [], "columns": {}}
    
    # 解析表头
    headers = [h.strip().strip('"') for h in lines[0].split(',')]
    
    # 解析数据行
    data = []
    for line in lines[1:]:
        if line.strip():
            values = [v.strip().strip('"') for v in line.split(',')]
            if len(values) == len(headers):
                row = {}
                for i, header in enumerate(headers):
                    value = values[i]
                    # 尝试转换为数字
                    try:
                        row[header] = float(value) if '.' in value else int(value)
                    except:
                        row[header] = value
                data.append(row)
    
    # 推断列类型
    columns = {}
    if data:
        for header in headers:
            sample_value = data[0].get(header)
            columns[header] = "number" if isinstance(sample_value, (int, float)) else "string"
    
    return {"data": data, "columns": columns}


def parse_table_data(table_text: str) -> Dict[str, Any]:
    """解析表格格式数据 (markdown table)"""
    lines = table_text.strip().split('\n')
    data_lines = [line for line in lines if '|' in line and not all(c in '|-: ' for c in line)]
    
    if len(data_lines) < 2:
        return {"data": [], "columns": {}}
    
    # 解析表头
    headers = [h.strip() for h in data_lines[0].split('|') if h.strip()]
    
    # 解析数据
    data = []
    for line in data_lines[1:]:
        values = [v.strip() for v in line.split('|') if v.strip()]
        if len(values) == len(headers):
            row = {}
            for i, header in enumerate(headers):
                value = values[i]
                # 尝试转换为数字
                try:
                    row[header] = float(value) if '.' in value else int(value)
                except:
                    row[header] = value
            data.append(row)
    
    # 推断列类型
    columns = {}
    if data:
        for header in headers:
            sample_value = data[0].get(header)
            columns[header] = "number" if isinstance(sample_value, (int, float)) else "string"
    
    return {"data": data, "columns": columns}


def parse_descriptive_data(text: str) -> Dict[str, Any]:
    """解析描述性数据"""
    # 提取数字和标签的模式
    patterns = [
        r'(\w+)[：:]\s*(\d+(?:\.\d+)?)',  # 标签: 数字
        r'(\w+)\s*(\d+(?:\.\d+)?)',      # 标签 数字
        r'(\d+(?:\.\d+)?)\s*(\w+)',      # 数字 标签
    ]
    
    data = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            for match in matches:
                if pattern == r'(\d+(?:\.\d+)?)\s*(\w+)':
                    # 数字在前
                    value, label = match
                else:
                    # 标签在前
                    label, value = match
                
                try:
                    numeric_value = float(value) if '.' in value else int(value)
                    data.append({"name": label, "value": numeric_value})
                except:
                    continue
            break
    
    if not data:
        # 如果没有找到模式，返回示例数据
        data = [{"name": "数据", "value": 1}]
    
    return {
        "data": data,
        "columns": {"name": "string", "value": "number"}
    }


def auto_select_chart_type(data: Dict[str, Any], requirements: str = "") -> str:
    """智能选择图表类型"""
    records = data.get("data", [])
    columns = data.get("columns", {})
    
    if not records:
        return "bar"
    
    # 根据需求关键词选择
    requirements_lower = requirements.lower()
    
    if any(keyword in requirements_lower for keyword in ["趋势", "时间", "变化", "时序", "timeline"]):
        return "line"
    elif any(keyword in requirements_lower for keyword in ["占比", "比例", "构成", "分布", "pie"]):
        return "pie"
    elif any(keyword in requirements_lower for keyword in ["散点", "相关", "关系", "scatter"]):
        return "scatter"
    elif any(keyword in requirements_lower for keyword in ["雷达", "多维", "radar"]):
        return "radar"
    elif any(keyword in requirements_lower for keyword in ["漏斗", "转化", "funnel"]):
        return "funnel"
    elif any(keyword in requirements_lower for keyword in ["仪表", "指标", "gauge"]):
        return "gauge"
    
    # 根据数据特征选择
    numeric_columns = [k for k, v in columns.items() if v == "number"]
    string_columns = [k for k, v in columns.items() if v == "string"]
    
    # 如果只有一个数值列和一个字符列，适合饼图或柱状图
    if len(numeric_columns) == 1 and len(string_columns) == 1:
        if len(records) <= 10:
            return "pie"
        else:
            return "bar"
    
    # 如果有多个数值列，适合折线图或柱状图
    elif len(numeric_columns) > 1:
        return "line"
    
    # 默认返回柱状图
    return "bar"


def generate_chart_config(data: Dict[str, Any], chart_type: str, title: str, requirements: str) -> Dict[str, Any]:
    """生成具体的图表配置"""
    records = data.get("data", [])
    columns = data.get("columns", {})
    
    if not records:
        return generate_empty_chart_config(title)
    
    # 基础配置
    config = {
        "title": {
            "text": title or f"{chart_type.upper()}图表",
            "left": "center",
            "textStyle": {
                "fontSize": 16,
                "fontWeight": "bold"
            }
        },
        "tooltip": {
            "trigger": "item" if chart_type in ["pie", "gauge"] else "axis",
            "backgroundColor": "rgba(50,50,50,0.7)",
            "borderColor": "#777",
            "borderWidth": 1,
            "textStyle": {
                "color": "#fff"
            }
        },
        "legend": {
            "top": "10%",
            "left": "center"
        },
        "toolbox": {
            "show": True,
            "feature": {
                "saveAsImage": {"show": True, "title": "保存为图片"},
                "restore": {"show": True, "title": "还原"},
                "dataView": {"show": True, "title": "数据视图"}
            }
        }
    }
    
    # 根据图表类型生成具体配置
    if chart_type == "bar":
        config.update(generate_bar_config(records, columns))
    elif chart_type == "line":
        config.update(generate_line_config(records, columns))
    elif chart_type == "pie":
        config.update(generate_pie_config(records, columns))
    elif chart_type == "scatter":
        config.update(generate_scatter_config(records, columns))
    elif chart_type == "radar":
        config.update(generate_radar_config(records, columns))
    elif chart_type == "funnel":
        config.update(generate_funnel_config(records, columns))
    elif chart_type == "gauge":
        config.update(generate_gauge_config(records, columns))
    else:
        config.update(generate_bar_config(records, columns))
    
    return config


def generate_bar_config(records: List[Dict], columns: Dict) -> Dict:
    """生成柱状图配置"""
    numeric_cols = [k for k, v in columns.items() if v == "number"]
    string_cols = [k for k, v in columns.items() if v == "string"]
    
    if not numeric_cols:
        return {}
    
    # 获取类别和数值
    category_col = string_cols[0] if string_cols else "index"
    value_col = numeric_cols[0]
    
    categories = []
    values = []
    
    for record in records:
        if category_col == "index":
            categories.append(f"项目{len(categories) + 1}")
        else:
            categories.append(str(record.get(category_col, "")))
        values.append(record.get(value_col, 0))
    
    return {
        "xAxis": {
            "type": "category",
            "data": categories,
            "axisLabel": {
                "rotate": 45 if len(max(categories, key=len)) > 4 else 0
            }
        },
        "yAxis": {
            "type": "value"
        },
        "series": [{
            "data": values,
            "type": "bar",
            "itemStyle": {
                "color": "#5470c6"
            },
            "emphasis": {
                "itemStyle": {
                    "color": "#91cc75"
                }
            }
        }],
        "grid": {
            "left": "3%",
            "right": "4%",
            "bottom": "3%",
            "containLabel": True
        }
    }


def generate_line_config(records: List[Dict], columns: Dict) -> Dict:
    """生成折线图配置"""
    numeric_cols = [k for k, v in columns.items() if v == "number"]
    string_cols = [k for k, v in columns.items() if v == "string"]
    
    if not numeric_cols:
        return {}
    
    category_col = string_cols[0] if string_cols else "index"
    
    categories = []
    series_data = {}
    
    # 初始化系列数据
    for col in numeric_cols:
        series_data[col] = []
    
    for record in records:
        if category_col == "index":
            categories.append(f"点{len(categories) + 1}")
        else:
            categories.append(str(record.get(category_col, "")))
        
        for col in numeric_cols:
            series_data[col].append(record.get(col, 0))
    
    # 生成系列配置
    series = []
    colors = ["#5470c6", "#91cc75", "#fac858", "#ee6666", "#73c0de", "#3ba272", "#fc8452", "#9a60b4"]
    
    for i, (col, data) in enumerate(series_data.items()):
        series.append({
            "name": col,
            "type": "line",
            "data": data,
            "smooth": True,
            "itemStyle": {
                "color": colors[i % len(colors)]
            }
        })
    
    return {
        "xAxis": {
            "type": "category",
            "data": categories
        },
        "yAxis": {
            "type": "value"
        },
        "series": series,
        "grid": {
            "left": "3%",
            "right": "4%",
            "bottom": "3%",
            "containLabel": True
        }
    }


def generate_pie_config(records: List[Dict], columns: Dict) -> Dict:
    """生成饼图配置"""
    numeric_cols = [k for k, v in columns.items() if v == "number"]
    string_cols = [k for k, v in columns.items() if v == "string"]
    
    if not numeric_cols:
        return {}
    
    name_col = string_cols[0] if string_cols else None
    value_col = numeric_cols[0]
    
    pie_data = []
    for i, record in enumerate(records):
        name = record.get(name_col, f"项目{i + 1}") if name_col else f"项目{i + 1}"
        value = record.get(value_col, 0)
        pie_data.append({"name": str(name), "value": value})
    
    return {
        "series": [{
            "name": "数据",
            "type": "pie",
            "radius": "50%",
            "data": pie_data,
            "emphasis": {
                "itemStyle": {
                    "shadowBlur": 10,
                    "shadowOffsetX": 0,
                    "shadowColor": "rgba(0, 0, 0, 0.5)"
                }
            },
            "label": {
                "show": True,
                "formatter": "{b}: {c} ({d}%)"
            }
        }]
    }


def generate_scatter_config(records: List[Dict], columns: Dict) -> Dict:
    """生成散点图配置"""
    numeric_cols = [k for k, v in columns.items() if v == "number"]
    
    if len(numeric_cols) < 2:
        return generate_bar_config(records, columns)
    
    x_col = numeric_cols[0]
    y_col = numeric_cols[1]
    
    scatter_data = []
    for record in records:
        x_val = record.get(x_col, 0)
        y_val = record.get(y_col, 0)
        scatter_data.append([x_val, y_val])
    
    return {
        "xAxis": {
            "type": "value",
            "name": x_col
        },
        "yAxis": {
            "type": "value",
            "name": y_col
        },
        "series": [{
            "data": scatter_data,
            "type": "scatter",
            "symbolSize": 8,
            "itemStyle": {
                "color": "#5470c6"
            }
        }],
        "grid": {
            "left": "3%",
            "right": "4%",
            "bottom": "3%",
            "containLabel": True
        }
    }


def generate_radar_config(records: List[Dict], columns: Dict) -> Dict:
    """生成雷达图配置"""
    numeric_cols = [k for k, v in columns.items() if v == "number"]
    
    if len(numeric_cols) < 3:
        return generate_bar_config(records, columns)
    
    # 计算最大值用于雷达图缩放
    max_values = {}
    for col in numeric_cols:
        max_values[col] = max([record.get(col, 0) for record in records])
    
    # 雷达图指标
    indicator = []
    for col in numeric_cols:
        indicator.append({
            "name": col,
            "max": max_values[col] * 1.2
        })
    
    # 雷达图数据
    radar_data = []
    for i, record in enumerate(records):
        values = [record.get(col, 0) for col in numeric_cols]
        radar_data.append({
            "value": values,
            "name": f"数据{i + 1}"
        })
    
    return {
        "radar": {
            "indicator": indicator
        },
        "series": [{
            "name": "雷达图",
            "type": "radar",
            "data": radar_data
        }]
    }


def generate_funnel_config(records: List[Dict], columns: Dict) -> Dict:
    """生成漏斗图配置"""
    numeric_cols = [k for k, v in columns.items() if v == "number"]
    string_cols = [k for k, v in columns.items() if v == "string"]
    
    if not numeric_cols:
        return {}
    
    name_col = string_cols[0] if string_cols else None
    value_col = numeric_cols[0]
    
    funnel_data = []
    for i, record in enumerate(records):
        name = record.get(name_col, f"阶段{i + 1}") if name_col else f"阶段{i + 1}"
        value = record.get(value_col, 0)
        funnel_data.append({"name": str(name), "value": value})
    
    # 按数值降序排列
    funnel_data.sort(key=lambda x: x["value"], reverse=True)
    
    return {
        "series": [{
            "name": "漏斗图",
            "type": "funnel",
            "left": "10%",
            "top": 60,
            "width": "80%",
            "minSize": "0%",
            "maxSize": "100%",
            "sort": "descending",
            "gap": 2,
            "label": {
                "show": True,
                "position": "inside"
            },
            "data": funnel_data
        }]
    }


def generate_gauge_config(records: List[Dict], columns: Dict) -> Dict:
    """生成仪表盘配置"""
    numeric_cols = [k for k, v in columns.items() if v == "number"]
    
    if not numeric_cols:
        return {}
    
    # 取第一个数值作为仪表盘显示
    value = records[0].get(numeric_cols[0], 0) if records else 0
    max_value = max([record.get(numeric_cols[0], 0) for record in records]) * 1.2
    
    return {
        "series": [{
            "name": "仪表盘",
            "type": "gauge",
            "detail": {
                "formatter": "{value}"
            },
            "data": [{
                "value": value,
                "name": numeric_cols[0]
            }],
            "max": max_value
        }]
    }


def generate_empty_chart_config(title: str) -> Dict:
    """生成空数据的默认图表配置"""
    return {
        "title": {
            "text": title or "暂无数据",
            "left": "center"
        },
        "xAxis": {
            "type": "category",
            "data": []
        },
        "yAxis": {
            "type": "value"
        },
        "series": [{
            "data": [],
            "type": "bar"
        }]
    }


# 创建 LangChain 工具
chart_generation_tool = Tool(
    name="generate_echarts_chart",
    description="""
    ECharts图表生成工具 - 根据数据和需求生成图表JSON配置
    
    参数:
    - data_input (str): 数据输入，支持多种格式:
      * JSON格式: [{"name": "A", "value": 100}, {"name": "B", "value": 200}]
      * CSV格式: "名称,数值\nA,100\nB,200"
      * 表格格式: "| 名称 | 数值 |\n| A | 100 |\n| B | 200 |"
      * 描述性文本: "销售额: 1000万, 利润: 200万"
    
    - chart_type (str, 可选): 图表类型
      * auto: 自动选择 (默认)
      * bar: 柱状图
      * line: 折线图
      * pie: 饼图
      * scatter: 散点图
      * radar: 雷达图
      * funnel: 漏斗图
      * gauge: 仪表盘
    
    - chart_title (str, 可选): 图表标题
    
    - analysis_requirements (str, 可选): 分析要求和图表需求描述
      * 可以包含关键词如"趋势"、"占比"、"相关性"等来辅助图表类型选择
    
    功能:
    - 智能解析多种数据格式
    - 自动选择最适合的图表类型
    - 生成完整的ECharts配置JSON
    - 支持图表样式自定义
    - 提供数据统计信息
    
    返回包含以下信息的JSON:
    - success: 是否成功
    - chart_type: 选择的图表类型
    - chart_config: 完整的ECharts配置JSON
    - data_summary: 数据摘要信息
    
    支持的图表类型:
    - 柱状图(bar): 适合分类数据比较
    - 折线图(line): 适合趋势分析
    - 饼图(pie): 适合占比分析
    - 散点图(scatter): 适合相关性分析
    - 雷达图(radar): 适合多维度分析
    - 漏斗图(funnel): 适合转化分析
    - 仪表盘(gauge): 适合单一指标展示
    
    重要提醒: 使用此工具的智能体必须用中文回答所有问题和分析结果
    """,
    func=generate_echarts_chart
)