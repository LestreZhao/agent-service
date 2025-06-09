{
    "chart_type": "柱状图",
    "chart_data": {
        "title": {
            "text": "糖尿病患者HbA1c水平分布",
            "left": "center"
        },
        "tooltip": {
            "trigger": "axis"
        },
        "legend": {
            "data": ["HbA1c水平"],
            "top": "10%"
        },
        "xAxis": {
            "type": "category",
            "data": ["左戋", "魏华", "陈金龙"]
        },
        "yAxis": {
            "type": "value",
            "name": "HbA1c (%)",
            "min": 5,
            "max": 11
        },
        "series": [
            {
                "name": "HbA1c水平",
                "type": "bar",
                "data": [9.9, 6.5, 5.9],
                "itemStyle": {
                    "color": function(params) {
                        const colors = ['#d83b4f', '#f28c28', '#4caf50'];
                        if (params.value >= 9) return colors[0];
                        if (params.value >= 6.5) return colors[1];
                        return colors[2];
                    }
                }
            }
        ]
    },
    "description": "该柱状图展示了三位糖尿病患者的糖化血红蛋白（HbA1c）水平分布。左戋的HbA1c值高达9.9%，显著高于正常范围，表明血糖控制极差，需优先干预。魏华的HbA1c为6.5%，处于临界值，提示需要进一步观察和管理。陈金龙的HbA1c为5.9%，在正常范围内，但仍需持续监测以维持健康状态。建议对不同患者采取分层管理策略，重点加强对高危患者的随访频率和干预力度。"
}