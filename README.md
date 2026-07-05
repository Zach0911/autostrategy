# Autostrategy

> AI 驱动的量化策略自动生成工具。输入策略需求 → Agent 设计 → 代码生成 → 回测验证 → 自主优化。

[![Skill](https://img.shields.io/badge/Skill-autostrategy-blue)](https://github.com/rivar0107/autostrategy)
[![Market](https://img.shields.io/badge/Market-A%E8%82%A1%20%7C%20%E6%B8%AF%E8%82%A1%20%7C%20%E7%BE%8E%E8%82%A1-green)]()
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

> ⚠️ **免责声明**：本工具生成的策略仅供学习和研究用途，不构成任何投资建议。量化交易有风险，过往回测表现不代表未来收益。

## 快速开始（产品版）

```bash
# 安装开发版
pip install -e .

# 初始化本地配置，会创建 ~/.autostrategy/settings.yaml
autostrategy config init

# 配置 LLM。API key 不写入配置文件，只从环境变量读取
autostrategy config set llm.provider openai
autostrategy config set llm.model gpt-4o-mini
export AUTOSTRATEGY_LLM_API_KEY="你的 API Key"

# 创建策略工作区
autostrategy strategy create dual-ma --template dual-ma

# 查看策略路径
autostrategy strategy paths dual-ma

# 用自然语言生成 STRATEGY_DESIGN.md，需要已配置 LLM key
autostrategy design create \
  --prompt "帮我做一个 A 股双均线策略" \
  --name dual-ma \
  --template dual-ma

# 从 STRATEGY_DESIGN.md 生成 strategy.py/config.yaml/README.md 等文件
autostrategy codegen create dual-ma --force

# 执行本地回测并生成 backtest/results/backtest_result.json
autostrategy backtest run dual-ma

# 查看策略状态，应从 draft/designed/coded 流转到 backtested
autostrategy strategy show dual-ma
```

> `design create` 和 `codegen create` 会调用用户自己配置的 LLM Provider。开源项目不会内置 API key，也不会替用户付费。

## 本地 Web / REST API / MCP（Phase 4A-4B）

Phase 4A 将 autostrategy 从纯 CLI 扩展为本地 Agent 服务平台骨架：CLI、REST API、Dashboard 和 MCP 工具复用同一套 service layer。

Phase 4B 将 Dashboard 升级为基于 **Ant Design 官方组件与默认主题** 的浏览器工作台。Web 端使用 React + Vite + TypeScript + `antd`，不引入 Tailwind、Bootstrap、shadcn/ui 或其他主题系统。

### 安装 Phase 4A/4B 依赖

```bash
# Python 侧：包含测试、API、Web Dashboard、MCP adapter
pip install -e ".[dev,api,web,mcp]"

# 前端侧：安装 Ant Design React 工作台依赖
npm install
npm run build
```

### 前端开发命令

```bash
# 开发服务器，仅用于前端迭代
npm run dev

# 构建到 src/autostrategy/web/static，由 autostrategy serve 托管
npm run build

# 运行前端测试
npm test
```

### 启动本地服务

```bash
autostrategy serve --host 127.0.0.1 --port 8000
```

启动后可访问：

| 地址 | 用途 |
|------|------|
| `http://127.0.0.1:8000/` | Ant Design 本地策略工作台 |
| `http://127.0.0.1:8000/docs` | FastAPI OpenAPI 文档 |
| `http://127.0.0.1:8000/api/v1/health` | 健康检查 |
| `http://127.0.0.1:8000/api/v1/strategies` | 策略列表 API |
| `http://127.0.0.1:8000/api/v1/templates` | 内置模板 API |

也可以指定工作区：

```bash
autostrategy serve --workspace-root /path/to/strategies
```

> 默认仅建议监听 `127.0.0.1`。Phase 4A 是本地优先能力，不提供多用户鉴权和远程托管安全边界。

### REST API 示例

```bash
# 健康检查
curl http://127.0.0.1:8000/api/v1/health

# 创建策略工作区
curl -X POST http://127.0.0.1:8000/api/v1/strategies \
  -H "Content-Type: application/json" \
  -d '{"name":"phase4a-demo","market":"A股","template":"dual-ma"}'

# 查看策略详情
curl http://127.0.0.1:8000/api/v1/strategies/phase4a-demo

# 查看策略 artifact 状态
curl http://127.0.0.1:8000/api/v1/strategies/phase4a-demo/artifacts

# 预览设计文档
curl http://127.0.0.1:8000/api/v1/strategies/phase4a-demo/artifacts/design

# 运行回测（需要 strategy.py 已存在）
curl -X POST http://127.0.0.1:8000/api/v1/strategies/phase4a-demo/backtest
```

### MCP 工具范围

Phase 4A 提供保守的 MCP adapter，主要用于本地 Agent 读取策略状态和触发低风险操作：

- `list_strategies`
- `get_strategy`
- `get_strategy_paths`
- `list_templates`
- `get_backtest_result`
- `create_strategy`
- `run_backtest`

暂不开放 `design_strategy` / `codegen_strategy` 作为 MCP 工具，避免其他 Agent 自动形成“生成代码 → 执行代码”的高风险链路。

### Phase 4A 安全边界

- API/MCP 只能通过 strategy slug 访问当前 workspace 内文件。
- `Workspace` 会拒绝 `../`、绝对路径等 path traversal。
- `CodegenAgent` 会拒绝明显危险的生成代码模式，例如 `os.system`、`subprocess`、`eval(`、`exec(`。
- 回测仍会在本地执行策略代码；这是本地研究工具，不是远程沙箱服务。

## 它能做什么？

| 入口 | 你说 | 它做 |
|------|------|------|
| **明确需求** | "帮我设计一个双均线交叉策略" | 直接分析 → 设计文档 → 代码 + 回测 |
| **模糊需求** | "我想做A股量化，但不确定用什么方法" | 诊断推荐 → 选方向 → 生成策略 |
| **博主策略** | "按某大V的投资逻辑做个策略" | 互联网研究 → 提炼逻辑 → 量化策略 |
| **优化迭代** | "优化这个策略的回测结果" | 诊断弱点 → 5轮自主优化 → 输出报告 |

## 核心设计

### 文档驱动

**STRATEGY_DESIGN.md 是「系统施工图纸」** — 所有策略逻辑先落在设计文档上，代码只是文档的严格翻译产物。

```
用户需求 → STRATEGY_DESIGN.md（精确规格）→ strategy.py（严格翻译）→ 回测验证
```

这意味着：AI 不会「自由发挥」，每行代码都有文档对应；修改策略时改文档，代码跟随更新。

### Agent 化工作流

Autostrategy 采用**多 Agent 串联**架构，用户只需在 3 个关键审批点参与决策：

```
用户输入
    ↓
┌─────────────────┐  Phase 1: 策略设计 Agent
│  设计 Agent      │  → 产出 STRATEGY_DESIGN.md
│  (design_agent)  │
└────────┬────────┘
         ↓ ⏸ 审批点 1：确认设计文档
┌─────────────────┐  Phase 2: 代码生成 Agent
│  代码 Agent      │  → 产出 strategy.py + 回测报告
│  (codegen_agent) │
└────────┬────────┘
         ↓ ⏸ 审批点 2：确认回测结果
┌─────────────────┐  Phase 3: 优化 Agent（自主/交互式）
│  优化 Agent      │  → 产出优化报告
│  (optimization)  │
└────────┬────────┘
         ↓ ⏸ 审批点 3：最终决策（接受 / 重做 / 回 Phase 1）
```

- **文件驱动状态转移**：STRATEGY_DESIGN.md → strategy.py → backtest_result.json → changelog.md
- **棘轮决策**：每次优化用 `score_strategy()` 评分，有效保留、无效回滚

## 适用市场

| 市场 | 数据源 | 交易规则 |
|------|--------|---------|
| **A股** | [FTShare](https://github.com/rivar0107/all-in-one)（免费） | T+1，涨跌停 ±10%/±20% |
| **港股** | FutuAPI（需 Futu OpenD） | T+0，无涨跌停 |
| **美股** | FutuAPI（需 Futu OpenD） | T+0，PDT 规则 |

> 期货、期权暂不支持，后续版本逐步加入。

## 快速开始

### 安装

```bash
npx skills add rivar0107/autostrategy --yes
```

安装后在 Claude Code / Gemini CLI / Copilot CLI 中直接使用，无需额外配置。

### 环境准备（可选）

```bash
pip install numpy pandas pyyaml
```

- **A股数据**：安装 [ftshare-all-in-one](https://github.com/rivar0107/all-in-one) Skill（免费）
- **港美股数据**：安装 FutuAPI Skill（需 [Futu OpenD](https://www.futunn.com/download/openAPI)）

### 使用示例

```
"帮我设计一个双均线交叉策略"
"我想做一个港股量化策略，但不清楚用什么方法"
"帮我根据某大V在微博上的投资观点做个量化策略"
"优化这个策略的回测结果，降低最大回撤"
```

## 项目结构

```
autostrategy/
├── pyproject.toml                     # Python 包定义与 CLI 入口
├── SKILL.md                           # 兼容旧 Skill 安装路径的 shim
├── src/autostrategy/
│   ├── cli/main.py                    # Typer CLI
│   ├── config.py                      # 本地配置与 LLM Provider 配置
│   ├── llm/client.py                  # OpenAI-compatible LLM Client
│   ├── agents/
│   │   ├── design_agent.py            # 自然语言 → STRATEGY_DESIGN.md
│   │   └── codegen_agent.py           # STRATEGY_DESIGN.md → strategy.py/config/README
│   ├── core/
│   │   ├── strategy.py                # Strategy 领域模型与状态
│   │   ├── workspace.py               # 策略工作区 CRUD 与文件 API
│   │   ├── template_registry.py       # 内置模板市场
│   │   └── backtest_engine.py         # 可导入的产品化回测引擎
│   └── templates/                     # dual-ma / grid / momentum 模板
├── .claude/skills/autostrategy/       # Claude Code Skill 兼容层
│   └── prompts/                       # 原 Skill prompts
├── scripts/
│   ├── env_setup.py                   # 环境检查与依赖安装
│   ├── quality_check.py               # 旧版策略设计文档质量检查
│   └── run_backtest.py                # 兼容脚本入口
├── examples/
│   └── dynamic-grid-multi-market/     # 示例：动态网格多标的策略
└── tests/                             # unit / integration 测试
```

## 示例策略

内置「动态网格多标的」策略示例，覆盖 5 个跨市场标的（腾讯、科创50ETF、中证2000ETF、小鹏、特斯拉）。

2024-2025 回测：年化收益 11.99%，最大回撤 30.47%，夏普 0.49，胜率 75.2%。

## 评估与设计原则

**评分函数**：5 个维度共 100 分 + 简洁性惩罚（条件数 > 10 时每个扣 1.5 分）。

| 维度 | 满分 | 满分条件 | 设计原则 |
|------|------|---------|---------|
| 年化收益率 | 25 | > 基准×2（沪深300 8% / 恒生 5% / 标普 10%）| 简洁性优先：分数提升必须大于复杂度增加 |
| 最大回撤 | 20 | < 10%（回撤≥30%得0分）| 文档是核心：所有逻辑先写入 DESIGN.md |
| 夏普比率 | 25 | > 2.0 | 人在回路：设计文档和回测结果人类确认 |
| 胜率 | 15 | > 60% | 量化评估：用 score_strategy() 决定 keep/revert |
| 盈亏比 | 15 | > 2.5 | 不推实盘：定位是策略创建和验证工具 |

同时检测：过拟合、幸存者偏差、未来函数、流动性、前后半段稳定性。

## 技术栈

- **语言**：Python 3.11+
- **CLI**：Typer
- **配置/数据模型**：Pydantic + PyYAML
- **数据处理**：NumPy, Pandas
- **回测**：函数式 `run_backtest(config)` 优先，兼容 Backtrader Strategy class
- **数据源**：[FTShare](https://github.com/rivar0107/all-in-one)（A股）、FutuAPI（港美股）、akshare/yfinance 等可扩展源
- **LLM Provider**：OpenAI-compatible，本地读取用户环境变量中的 API key
- **AI Agent 兼容**：Claude Code, Gemini CLI, Copilot CLI, Codex, Cline 等

## 相关项目

- [all-in-one](https://github.com/rivar0107/all-in-one) — 免费的 A 股/港股行情数据 Skill
- [darwin-skill](https://github.com/alchaincyf/darwin-skill) — AI Skill 持续优化框架

## License

MIT License
