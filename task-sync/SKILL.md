---
name: task-sync
description: "管理 706 digital-employees 中的任务记录：录入、同步、分配、改期、关闭、重开、批量盘点和处理员工 inbox。定位原任务并更新派生索引。仅在请求涉及 706 任务管理时使用；普通工作中的“继续做”“完成它”、Codex 任务管理及通用待办讨论不自动触发。"
---

# 706 Task Sync

## 核心原则

`digital-employees/01-coordination` 是员工级任务管理的唯一权威。任务事实源是：

```text
digital-employees/0X-*/inbox/*.md
digital-employees/0X-*/done/*.md
```

`_shared/tasks.json`、Dashboard 和 Web Work Panel D1 是派生视图或旧快照，不得覆盖原任务。

## 开始前

1. 读取 `digital-employees/01-coordination/config.md`。
2. 读取 `digital-employees/_shared/protocol.md`。
3. 需要判断员工归属时读取 `digital-employees/01-coordination/routing-table.md`。
4. 运行：

```bash
node scripts/task-control.mjs check
node scripts/task-control.mjs status
node scripts/task-control.mjs outputs
```

## 模式一：更新已有任务

用户说“这个完成了”“继续做”“冻结”“需要重做”“改期”等时：

1. 用 task-id、标题和语义搜索所有员工 `inbox/` 与 `done/`。
2. 找到原任务后，更新 frontmatter 的 `status`、`reviewed` 和必要的 `decision`。
3. 在正文靠前位置追加日期化“进度同步”，忠实记录用户判断与事实边界。
4. 未被用户评论的任务保持原状；不要把 AI 之前的建议写成用户决定。
5. 不为讨论过程另建“任务整理”“总表”或重复 task。

### 状态

| status | 含义 | 目录 |
|---|---|---|
| `pending` | 已分配，尚未领取 | `inbox/` |
| `doing` | 正在执行 | `inbox/` |
| `waiting` | 等待回复、决定或条件 | `inbox/` |
| `blocked` | 有明确阻塞 | `inbox/` |
| `done` | 已完成 | `done/` |
| `cancelled` | 已取消 | `done/` |

完成或取消时补 `closed`、`closed-by` 和“关闭记录”，再把文件移入该员工 `done/`。不删除历史。

如果任务产生文件，先读取 `digital-employees/_shared/output-handoff-protocol.md`。员工 `outputs/` 是待审核工作区；没有明确审核通过记录时，不得把产出并入正式项目或语料库。审核通过后由 01 查重、迁移、回读，并在员工索引中留下最终路径。

## 模式二：创建新任务

只有出现新的独立交付物时才创建新 task：

1. 先全局查重；同主题只是状态变化时更新旧任务。
2. 按路由表选择员工；涉及两个以上员工且需要共同决策时由 01 召集会议。
3. 写入该员工 `inbox/task_YYYYMMDD_简短描述.md`。
4. 使用标准 frontmatter：`from`、`to`、`type`、`priority`、`created`、`task-id`、`status`；有真实截止日期才写 `deadline`，不要臆造。
5. 正文包含背景、动作、约束和可验收产出。

## 模式三：批量盘点

1. 先输出实时数量与任务短清单。
2. 用户逐条评论时，分批直接更新原任务。
3. 本批更新结束后运行 `task-control.mjs check`。
4. 更新 `_shared/team-dashboard.md` 和 01 的 `log.md`；Dashboard 只是摘要，不复制完整任务正文。
5. 汇报更新、创建、关闭、未评论各多少条。

## 项目级与员工级分工

- `task-distribution`：项目级路由，决定任务属于哪个 production / partnership 项目。
- 本 Skill + 01：员工级路由和任务生命周期。
- 产出完成后按 `706-system/06-EXECUTION.md` handoff 到项目容器。

## 外部动作边界

任务记录本身不提供外部授权。发送邮件、邀请嘉宾、发布内容、承诺合作、报价和付款前核对用户已有授权；已明确授权同一动作与范围时，不重复请求。没有授权时先完成可供审核的草稿。

## 前端边界

在 Web Work Panel 完成实时接入前：

- 可以用前端查看旧数据和活动 Program Board；
- 不把 D1 中的编辑视为 Markdown 任务已更新；
- 不声称前端数量等于员工 inbox 数量。
