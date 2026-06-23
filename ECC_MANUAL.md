# ECC 完全使用手册

> ECC (Enhanced Claude Code) v1.10.0 — AI 编程助手全栈强化系统  
> 安装方式: `npm install -g ecc-universal` → `ecc install --profile full`

---

## 目录

1. [快速上手](#1-快速上手)
2. [命令参考 / Commands](#2-命令参考--commands)（79 个）
3. [技能参考 / Skills](#3-技能参考--skills)（204 个）
4. [Agent 参考](#4-agent-参考)（48 个）
5. [Rules 规则体系](#5-rules-规则体系)（89 个）
6. [Hooks 自动化钩子](#6-hooks-自动化钩子)
7. [多模型编排](#7-多模型编排)
8. [项目管理命令](#8-项目管理命令)

---

## 1. 快速上手

### 安装后的变化

重启 Claude Code 后，输入 `/` 会看到 79 个新命令。同时系统自动加载了：

- **Rules**: 89 个规则文件，覆盖通用编码规范 + 16 种语言专用规则
- **Skills**: 204 个技能，输入关键词时自动匹配激活
- **Agents**: 48 个专业 Agent，可在对话中随时调用

### 第一时间该做的

```bash
ecc doctor        # 检查安装是否完整
ecc status        # 查看 ECC 运行状态
```

---

## 2. 命令参考 / Commands（79 个）

所有命令通过在 Claude Code 中输入 `/命令名` 使用。

### 2.1 核心开发流程

| 命令 | 用途 | 示例 |
|------|------|------|
| `/code-review` | 代码审查（本地变更或 PR） | `/code-review` 或 `/code-review 42` |
| `/tdd` | 测试驱动开发 | `/tdd 实现用户登录` |
| `/plan` | 架构设计与实施计划 | `/plan 添加缓存层` |
| `/feature-dev` | 完整功能开发流程 | `/feature-dev 导出 PDF` |
| `/refactor-clean` | 重构清理 | `/refactor-clean` |
| `/verify` | 验证改动是否生效 | `/verify` |

### 2.2 多模型编排

| 命令 | 用途 |
|------|------|
| `/multi-plan` | 多模型并行规划（多个 AI 同时设计方案，选最优） |
| `/multi-execute` | 多模型并行执行 |
| `/multi-workflow` | 多模型复杂工作流 |
| `/multi-backend` | 多后端并行开发 |
| `/multi-frontend` | 多前端并行开发 |
| `/orchestrate` | 通用多 Agent 编排 |

### 2.3 项目启动

| 命令 | 用途 |
|------|------|
| `/blueprint` | 从零生成项目的完整 PRD + 架构蓝图 |
| `/init` | 为新项目初始化 ECC 配置 |
| `/spec` | 编写技术规格说明 |

### 2.4 构建与测试

| 命令 | 语言/框架 | 用途 |
|------|-----------|------|
| `/cpp-build` `/cpp-test` `/cpp-review` | C++ | 编译、测试、审查 |
| `/go-build` `/go-test` `/go-review` | Go | 编译、测试、审查 |
| `/kotlin-build` `/kotlin-test` `/kotlin-review` | Kotlin | 编译、测试、审查 |
| `/rust-build` `/rust-test` `/rust-review` | Rust | 编译、测试、审查 |
| `/flutter-build` `/flutter-test` `/flutter-review` | Flutter | 编译、测试、审查 |
| `/gradle-build` | JVM 系 | Gradle 构建 |
| `/e2e` | 通用 | 端到端测试 |
| `/test-coverage` | 通用 | 测试覆盖率分析 |

### 2.5 AI 工程专项

| 命令 | 用途 |
|------|------|
| `/claw` | Claude 自主长时工作循环 |
| `/agent-sort` | 按任务自动分配合适的 Agent |
| `/evolve` | 让 AI 自动迭代优化代码 |
| `/learn` `/learn-eval` | 让 AI 学习项目上下文 |
| `/prompt-optimize` | 优化 Prompt 效果 |
| `/model-route` | 按任务复杂度自动路由到不同模型 |
| `/context-budget` | 管理 Token 预算 |
| `/harness-audit` | 审计 harness 配置 |
| `/instinct-export` `/instinct-import` | 导出/导入 AI 学习经验 |
| `/prp-plan` `/prp-implement` `/prp-commit` `/prp-pr` | PRP 工作流四阶段 |
| `/prp-prd` | 生成产品需求文档 |

### 2.6 安全

| 命令 | 用途 |
|------|------|
| `/security-review` | 安全审查 |
| `/security-bounty-hunter` | 安全漏洞猎人模式 |

### 2.7 文档与知识

| 命令 | 用途 |
|------|------|
| `/docs` | 生成/更新文档 |
| `/update-docs` | 同步更新文档 |
| `/update-codemaps` | 更新代码地图 |
| `/code-tour` | 生成代码导读 |
| `/rules-distill` | 从代码中提炼规则 |

### 2.8 Hook 管理

| 命令 | 用途 |
|------|------|
| `/hookify` | 为所有规则自动生成 hooks |
| `/hookify-configure` | 配置 hooks |
| `/hookify-help` | Hooks 帮助 |
| `/hookify-list` | 列出所有 hooks |

### 2.9 会话与状态

| 命令 | 用途 |
|------|------|
| `/checkpoint` | 创建会话检查点 |
| `/save-session` | 保存当前会话 |
| `/resume-session` | 恢复之前会话 |
| `/sessions` | 查看所有会话 |
| `/loop-start` `/loop-status` | 启动/查看自主循环任务 |
| `/devfleet` | Dev fleet 管理 |
| `/aside` | 临时分支对话 |

### 2.10 项目管理

| 命令 | 用途 |
|------|------|
| `/projects` | 项目管理 |
| `/jira` | Jira 集成 |
| `/github-ops` | GitHub 操作 |

### 2.11 AI 工程进阶

| 命令 | 用途 |
|------|------|
| `/gan-build` `/gan-design` | 生成式开发 |
| `/council` | AI 委员会评审模式 |
| `/eval` | 评估 AI 产出质量 |
| `/quality-gate` | 质量门禁 |
| `/skill-create` `/skill-health` | 技能管理 |
| `/prune` | 清理无用上下文 |
| `/build-fix` | AI 驱动的构建修复 |
| `/pm2` | PM2 进程管理集成 |

---

## 3. 技能参考 / Skills（204 个）

Skills 在对话中**自动触发**，只需正常描述需求。以下按领域分类：

### 3.1 需求与规划（10 个）

| 技能 | 触发场景 |
|------|---------|
| `brainstorming` | 任何创新性工作前自动触发 |
| `blueprint` | 从零规划项目 |
| `spec` | 编写技术规格 |
| `plan-ceo-review` | CEO 视角产品评审 |
| `plan-eng-review` | 工程评审 |
| `plan-design-review` | 设计评审 |
| `plan-devex-review` | 开发者体验评审 |
| `plan-tune` | 优化计划 |
| `strategic-compact` | 战略压缩 |
| `investigate` | 深度调查问题 |

### 3.2 开发流程（15 个）

| 技能 | 触发场景 |
|------|---------|
| `tdd-workflow` | TDD 测试驱动 |
| `code-review` | 代码审查 |
| `deployment-patterns` | 部署模式 |
| `docker-patterns` | Docker 容器化 |
| `database-migrations` | 数据库迁移 |
| `e2e-testing` | 端到端测试 |
| `verification-loop` | 验证循环 |
| `agentic-engineering` | Agent 工程 |
| `ai-first-engineering` | AI 优先工程 |
| `autonomous-loops` | 自主循环 |
| `continuous-agent-loop` | 持续 Agent 循环 |
| `continuous-learning` / `v2` | 持续学习 |
| `cost-aware-llm-pipeline` | LLM 成本优化 |
| `prompt-optimizer` | Prompt 优化 |
| `search-first` | 搜索优先 |

### 3.3 语言专用（50+ 个）

| 语言 | 可用技能 |
|------|---------|
| **Python** | `python-patterns`, `python-testing`, `django-patterns`, `django-security`, `django-tdd`, `django-verification` |
| **TypeScript/JS** | `frontend-design`, `frontend-patterns`, `nestjs-patterns`, `nodejs-keccak256` |
| **Kotlin** | `kotlin-patterns`, `kotlin-testing`, `kotlin-coroutines-flows`, `kotlin-ktor-patterns`, `kotlin-exposed-patterns` |
| **Java/Spring** | `springboot-patterns`, `springboot-security`, `springboot-tdd`, `springboot-verification`, `jpa-patterns` |
| **Go** | `golang-patterns`, `golang-testing` |
| **Rust** | `rust-patterns`, `rust-testing` |
| **C++** | `cpp-coding-standards`, `cpp-testing` |
| **Swift/iOS** | `swiftui-patterns`, `swift-concurrency-6-2`, `swift-protocol-di-testing`, `swift-actor-persistence`, `ios-clean`, `ios-fix`, `ios-qa`, `ios-sync`, `ios-design-review` |
| **PHP/Laravel** | `laravel-patterns`, `laravel-security`, `laravel-tdd`, `laravel-plugin-discovery`, `laravel-verification` |
| **Perl** | `perl-patterns`, `perl-security`, `perl-testing` |
| **C#/.NET** | `dotnet-patterns`, `csharp-testing` |
| **Dart/Flutter** | `dart-flutter-patterns` |
| **Mobile** | `android-clean-architecture`, `compose-multiplatform-patterns` |

### 3.4 安全（8 个）

| 技能 | 触发场景 |
|------|---------|
| `security-review` | 安全审查 |
| `security-scan` | 自动化安全扫描 |
| `security-bounty-hunter` | 漏洞猎人 |
| `hipaa-compliance` | HIPAA 医疗合规 |
| `healthcare-phi-compliance` | 医疗 PHI 合规 |
| `defi-amm-security` | DeFi AMM 安全 |
| `llm-trading-agent-security` | LLM 交易 Agent 安全 |
| `careful` | 危险命令安全确认 |

### 3.5 API 与集成（8 个）

| 技能 | 触发场景 |
|------|---------|
| `claude-api` | Claude API / Anthropic SDK 开发 |
| `api-design` | API 设计 |
| `api-connector-builder` | API 连接器 |
| `mcp-server-patterns` | MCP Server 模式 |
| `x-api` | X/Twitter API |
| `exa-search` | Exa 搜索集成 |
| `jira-integration` | Jira 集成 |
| `github-ops` | GitHub 操作 |

### 3.6 内容与媒体（10 个）

| 技能 | 触发场景 |
|------|---------|
| `article-writing` | 文章撰写 |
| `remotion-video-creation` | Remotion 视频制作 |
| `manim-video` | Manim 数学动画 |
| `video-editing` | 视频剪辑 |
| `fal-ai-media` | fal.ai 媒体生成 |
| `liquid-glass-design` | Liquid Glass 设计风格 |
| `make-pdf` | PDF 生成 |
| `document-generate` | 文档生成 |
| `document-release` | 文档发布 |
| `investor-materials` | 投资人材料 |

### 3.7 业务与运营（15 个）

| 技能 | 触发场景 |
|------|---------|
| `market-research` | 市场调研 |
| `deep-research` | 深度研究报告 |
| `product-capability` | 产品能力分析 |
| `lead-intelligence` | 线索情报 |
| `seo` | SEO 优化 |
| `brand-voice` | 品牌声音 |
| `content-engine` | 内容引擎 |
| `social-graph-ranker` | 社交图谱排名 |
| `dashboard-builder` | 仪表盘构建 |
| `energy-procurement` | 能源采购 |
| `inventory-demand-planning` | 库存需求计划 |
| `logistics-exception-management` | 物流异常管理 |
| `production-scheduling` | 生产排程 |
| `quality-nonconformance` | 质量不合规 |
| `returns-reverse-logistics` | 退货逆向物流 |

### 3.8 开发运维（8 个）

| 技能 | 触发场景 |
|------|---------|
| `gstack` / `gstack-upgrade` | GStack 部署运维 |
| `gstack-command` | GStack 命令 |
| `setup-deploy` | 部署配置 |
| `setup-gbrain` | GBrain 配置 |
| `land-and-deploy` | 一键部署 |
| `canary` | 金丝雀发布监控 |
| `health` | 健康检查 |
| `qa` / `qa-only` | QA 测试 |

### 3.9 调试与问题定位（10 个）

| 技能 | 触发场景 |
|------|---------|
| `systematic-debugging` | 系统化调试 |
| `agent-introspection-debugging` | Agent 自查调试 |
| `ai-regression-testing` | AI 回归测试 |
| `benchmark` / `benchmark-models` | 性能基准测试 |
| `context-restore` / `context-save` | 上下文管理 |
| `freeze` / `unfreeze` | 冻结/恢复项目状态 |
| `investigate` | 深度排查 |
| `retro` | 回顾总结 |

---

## 4. Agent 参考（48 个）

Agent 是专门的 AI 子进程，可由命令或对话触发调用。

### 4.1 设计与规划

| Agent | 用途 |
|-------|------|
| `architect` | 系统架构设计 |
| `code-architect` | 代码架构设计 |
| `planner` | 实施计划制定 |
| `chief-of-staff` | 项目统筹协调 |
| `tdd-guide` | TDD 指导 |

### 4.2 代码审查（按语言）

| Agent | 语言 |
|-------|------|
| `code-reviewer` | 通用代码审查 |
| `typescript-reviewer` | TypeScript |
| `python-reviewer` | Python |
| `java-reviewer` | Java |
| `kotlin-reviewer` | Kotlin |
| `go-reviewer` | Go |
| `rust-reviewer` | Rust |
| `cpp-reviewer` | C++ |
| `csharp-reviewer` | C# |
| `dart-build-resolver` | Dart |
| `flutter-reviewer` | Flutter |
| `database-reviewer` | 数据库/SQL |

### 4.3 构建修复（按语言）

| Agent | 用途 |
|-------|------|
| `build-error-resolver` | 通用构建错误修复 |
| `go-build-resolver` | Go 构建修复 |
| `java-build-resolver` | Java 构建修复 |
| `kotlin-build-resolver` | Kotlin 构建修复 |
| `rust-build-resolver` | Rust 构建修复 |
| `cpp-build-resolver` | C++ 构建修复 |

### 4.4 质量与安全

| Agent | 用途 |
|-------|------|
| `security-reviewer` | 安全审查 |
| `performance-optimizer` | 性能优化 |
| `code-simplifier` | 代码简化 |
| `refactor-cleaner` | 重构清理 |
| `silent-failure-hunter` | 静默失败检测 |
| `type-design-analyzer` | 类型设计分析 |
| `pr-test-analyzer` | PR 测试分析 |
| `harness-optimizer` | Harness 优化 |
| `healthcare-reviewer` | 医疗合规审查 |

### 4.5 探索与知识

| Agent | 用途 |
|-------|------|
| `code-explorer` | 代码探索 |
| `docs-lookup` | 文档查询 |
| `doc-updater` | 文档更新 |
| `conversation-analyzer` | 对话分析 |
| `comment-analyzer` | 代码注释分析 |
| `seo-specialist` | SEO 专家 |
| `a11y-architect` | 无障碍架构 |

### 4.6 开源与自动化

| Agent | 用途 |
|-------|------|
| `opensource-forker` | 开源 Fork 辅助 |
| `opensource-packager` | 开源打包 |
| `opensource-sanitizer` | 开源敏感信息清理 |
| `loop-operator` | 循环任务执行 |
| `e2e-runner` | E2E 测试执行 |
| `gan-planner` / `gan-evaluator` / `gan-generator` | 生成式开发三部 |

---

## 5. Rules 规则体系（89 个）

Rules 在对话中**始终生效**，Claude Code 会严格遵守。

### 5.1 通用规则 (`rules/common/`)

| 规则 | 内容 |
|------|------|
| `agents.md` | Agent 使用规范 |
| `code-review.md` | 代码审查标准 |
| `coding-style.md` | 编码风格 |
| `development-workflow.md` | 开发工作流 |
| `git-workflow.md` | Git 工作流 |
| `hooks.md` | Hooks 配置规范 |
| `patterns.md` | 设计模式 |
| `performance.md` | 性能规范 |
| `security.md` | 安全规范 |
| `testing.md` | 测试规范 |

### 5.2 语言专用规则

| 语言 | 规则数 | 涵盖 |
|------|--------|------|
| **C++** | 5 | 编码风格、Hooks、模式、安全、测试 |
| **Python** | 5 | 编码风格、Hooks、模式、安全、测试 |
| **Go** | 5 | 编码风格、Hooks、模式、安全、测试 |
| **Java** | 5 | 编码风格、Hooks、模式、安全、测试 |
| **Kotlin** | 5 | 编码风格、Hooks、模式、安全、测试 |
| **Rust** | 5 | 编码风格、Hooks、模式、安全、测试 |
| **Swift** | 5 | 编码风格、Hooks、模式、安全、测试 |
| **TypeScript** | 5 | 编码风格、Hooks、模式、安全、测试 |
| **C#** | 5 | 编码风格、Hooks、模式、安全、测试 |
| **Dart** | 5 | 编码风格、Hooks、模式、安全、测试 |
| **PHP** | 5 | 编码风格、Hooks、模式、安全、测试 |
| **Perl** | 5 | 编码风格、Hooks、模式、安全、测试 |
| **Web** | 2 | 通用 Web 规范 |
| **中文 (zh)** | 2 | 中文项目规范 |

---

## 6. Hooks 自动化钩子

Hooks 在特定事件发生时自动执行脚本，位于 `~/.claude/hooks/`。

### 配置文件

- `hooks.json` — 主配置，定义触发事件和对应脚本
- `README.md` — Hooks 使用说明

### 管理命令

```text
/hookify            从规则自动生成 hooks
/hookify-configure  配置 hooks 行为
/hookify-list       列出所有已安装 hooks
/hookify-help       Hooks 帮助
```

---

## 7. 多模型编排

ECC 支持同时调用多个 AI 模型并行工作，然后合并最佳结果。

### 命令

```text
/multi-plan        # 多模型并行规划（多个方案 → 选最优）
/multi-execute     # 多模型并行执行
/multi-workflow    # 多模型工作流
/multi-backend     # 多后端并行开发
/multi-frontend    # 多前端并行开发
/orchestrate       # 通用多 Agent 编排
/council           # AI 委员会评审模式
```

### 使用场景

```
/multi-plan 设计用户认证系统架构
/council 评审这 3 个 API 设计方案
```

---

## 8. 项目管理命令

### 会话管理

```text
/save-session      保存当前会话
/resume-session    恢复之前会话
/sessions          查看所有保存的会话
/checkpoint        创建会话检查点
```

### 工作循环

```text
/loop-start        启动自主循环任务
/loop-status       查看循环任务状态
/devfleet          管理开发舰队
/aside             临时分支对话
```

### 持续学习

```text
/instinct-status   查看 AI 学习状态
/instinct-export   导出学习经验
/instinct-import   导入学习经验
/learn             让 AI 学习项目上下文
/learn-eval        评估学习效果
```

### Token 管理

```text
/context-budget    查看/设置 Token 预算
/prune             清理无用上下文
```

---

## 附录 A：安装与维护

### 安装

```powershell
npm install -g ecc-universal        # 安装 CLI
ecc catalog                         # 浏览可用 profiles
ecc install --profile full          # 安装完全版
```

### 日常维护

```powershell
ecc doctor                          # 诊断文件完整性
ecc repair                          # 修复缺失/偏离文件
ecc status                          # 查看运行状态
ecc list-installed                  # 列出已安装组件
```

### 卸载

```powershell
ecc uninstall                       # 卸载 ECC 管理文件
npm uninstall -g ecc-universal      # 卸载 CLI
```

---

## 附录 B：与 dm-chushihua-codex 项目结合使用

该项目是一个 Python Flask Web 应用，推荐常用以下命令：

```text
/code-review        # 每次改动后审查代码
/verify             # 验证改动是否生效
/tdd                # 添加新功能时用 TDD
/security-review    # 安全审查（尤其关注 SQL 注入等）
/blueprint          # 大功能规划
/python-review      # Python 专项审查
/docs               # 更新文档
```

---

> 版本: ECC v1.10.0 | 安装日期: 2026-06-04 | Profile: full（20 模块）
