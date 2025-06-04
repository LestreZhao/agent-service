# 变更日志

## [重构] 框架重命名 - FusionAI

### 主要更改

#### 1. 框架名称更新
- **原名称**: LangManus
- **新名称**: FusionAI
- **更改范围**: 所有文档、规则文件、提示词和配置

#### 2. 公司品牌信息
- **开发公司**: 湖北福鑫科创信息技术有限公司 (Hubei Fuxin Technology Innovation Co., Ltd.)
- **更新位置**: README、coordinator和reporter提示词文件

#### 3. README 文档更新
- 将英文 README.md 替换为中文版本
- 删除 README_zh.md（内容已合并到主 README）
- 更新所有项目描述和说明为中文
- 更新GitHub仓库链接为 fusionai/fusionai

#### 4. 提示词文件更新
更新了以下提示词文件中的品牌信息：

- `src/prompts/coordinator.md` - 将LangManus改为FusionAI，添加公司开发信息
- `src/prompts/reporter.md` - 添加FusionAI品牌信息和公司信息

#### 5. Cursor 规则文件更新
更新了以下规则文件中的框架名称：

- `.cursor/rules/README.mdc` - 规则总览
- `.cursor/rules/project-structure.mdc` - 项目结构指南
- `.cursor/rules/testing-and-quality.mdc` - 测试和代码质量规则
- `.cursor/rules/environment-setup.mdc` - 环境设置规则
- `.cursor/rules/langgraph-workflow.mdc` - LangGraph工作流规则
- `.cursor/rules/api-integration.mdc` - API集成规则
- `.cursor/rules/data-processing.mdc` - 数据处理规则
- `.cursor/rules/api-development.mdc` - API开发规范

#### 6. 新创建的规则文件
本次更新中创建了以下新的 Cursor 规则文件：

1. **testing-and-quality.mdc** - 测试和代码质量规则
   - 测试框架配置指南
   - 代码质量工具使用
   - 开发最佳实践

2. **environment-setup.mdc** - 环境设置和配置规则
   - Python 3.12 环境配置
   - uv 包管理器使用指南
   - 三层LLM系统配置
   - 常见问题解决方案

3. **langgraph-workflow.mdc** - LangGraph工作流开发规则
   - LangGraph架构概述
   - 工作流构建方法
   - 智能体集成模式
   - 状态管理和条件路由

4. **api-integration.mdc** - API集成和外部服务规则
   - LLM API集成模式
   - 搜索和网页抓取API配置
   - 浏览器自动化设置
   - API安全和错误处理

5. **data-processing.mdc** - 数据处理和分析规则
   - 数据处理框架使用指南
   - Python REPL工具配置
   - 金融数据分析
   - 数据库集成和性能优化

#### 7. 规则文件组织优化
将规则文件按功能分类：

- **核心架构**: 项目结构、工作流设计
- **环境配置**: 开发环境、依赖管理
- **开发规范**: 代码质量、测试规范
- **API集成**: 外部服务、接口设计
- **数据处理**: 数据分析、数据库集成
- **运维管理**: 故障处理、性能优化

### 保持不变的内容

- 项目的核心架构和功能
- 代码实现和逻辑
- 配置文件格式和结构
- API 接口设计
- 技术栈和依赖

### 后续需要更新的内容

1. **代码文件中的引用**
   - Python 文件中的注释和文档字符串
   - 配置文件中的项目名称引用
   - 日志信息中的项目名称

2. **Git 仓库信息**
   - 仓库名称和 URL
   - 贡献指南中的链接
   - 问题模板和 PR 模板

3. **部署配置**
   - Docker 镜像名称
   - 服务名称配置
   - 监控和日志配置

### 影响评估

- **文档一致性**: ✅ 已完成
- **开发体验**: ✅ 通过 Cursor 规则增强
- **向后兼容**: ✅ 核心功能保持不变
- **维护成本**: ⬇️ 通过规则文件降低

---

*此变更日志记录了框架从 LangManus 到 FusionAI 的重命名过程，以及相关文档和规则文件的更新。* 