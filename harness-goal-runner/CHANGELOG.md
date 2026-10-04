# Changelog

## v0.1.0 - 2026-06-13

- 新增 `harness-goal-runner` skill。
- 支持为个人端 Claude/DeepSeek CLI 工作流设计 `goal.md`、`checks.sh`、`run.sh`。
- 内置最小 shell runner 模板，默认 5 轮、预算 2 美元、每轮写入日志。

## 已知局限

- 第一版只提供 shell runner 模板，不实现完整 Node.js supervisor。
- `checks.sh` 的质量取决于具体任务能否给出清晰验收命令。
- 长时间无人值守任务仍建议另做队列、状态文件和通知机制。
