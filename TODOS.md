# TODOS

## Phase 5 — Paper Trading / 模拟盘

- **准实时 replay（Phase 5B）**
  - Priority: P1
  - 将 paper run 从一次性函数调用改为按 bar/day 逐步推进的长时任务
  - 每处理一个事件检查 stop_requested，周期性刷新 paper_run_result.json
  - 前端轮询展示持续更新的 progress、current_at、latest_decision
  - Status: 未开始

- **虚拟账户与持仓模型**
  - Priority: P2
  - 在 paper run 中维护 cash、positions、equity 状态
  - 支持 buy/sell/hold 决策落盘到 events
  - Status: 未开始

- **本地 mock 行情 feed**
  - Priority: P2
  - 接入历史行情数据作为 replay 数据源
  - 支持按时间窗口推进
  - Status: 未开始

## Completed

- **本地 API + MCP 工具接口** — Completed: v0.1.0.0 (2026-07-05)
- **Ant Design 浏览器工作台 + LLM 配置安全** — Completed: v0.1.0.0 (2026-07-05)
- **replay-first 模拟运行最小闭环** — Completed: v0.1.0.0 (2026-07-05)
