---
name: task-distribution
description: >
  706 任务分发系统。当用户说"任务分发""任务排序""工作安排"时触发。
  也可在 bootstrap 冷启动后、写入 INBOX 后自动触发。

  功能：读取 706-system/02-INBOX.md 中未处理条目 → 
  按 Inbox Sync Protocol 判断归属项目 → 
  写入该分项目的 system/current-state.md（## 当前任务 section）→ 
  标记 INBOX 条目为 ✅ → P0/P1 同步写入全局 04-TASKS.md。

  路由逻辑：显式项目名 > 关键词匹配（references/project-routes.md）> 上下文推断 > 
  多匹配询问用户 > 无法判断保留在 INBOX 待下次分类。
---

# 706 任务分发

## 你在做什么

你是 Inbox Sync Protocol 的**执行引擎**。Protocol 负责"记"（写 INBOX），你负责"分"（INBOX → 分项目）。

**一句话**：读 INBOX → 分类 → 写到分项目 current-state.md → 标记 ✅。

---

## 触发时机

| 触发 | 行为 |
|------|------|
| 用户说"任务分发""任务排序""工作安排" | 处理 INBOX 中所有未标记 ✅ 的条目 |
| 用户刚写完 INBOX（"帮我记一下"之后） | 立即分发刚写入的那条 |
| Bootstrap 冷启动扫描后 | 检查 INBOX 是否有未处理条目，有则分发 |

---

## Inbox Sync Protocol（协议原文，与 02-INBOX.md 一致）

1. 你通过微信/Telegram/iMessage/邮件/对话说了新信息 → Claude 写入 INBOX
2. 每条信息标注：`[来源] 谁说了什么` + `归属项目（判断）` + `紧急度`
3. 归属明确 → 由 `task-distribution` skill 分发到对应项目 `system/current-state.md`
4. 归属不明确 → 保留在 INBOX，等下次 task-distribution 再试
5. 已处理打 ✅，不删除
6. 每周过一遍未处理的 INBOX 条目

---

## 路由决策树

按优先级依次判断：

```
1. 显式项目名
   "七月活动要做XXX" → 706-production-event/2026-07-shanghai-future-community

2. 关键词匹配（见 references/project-routes.md）
   命中关键词 → 路由到对应项目

3. 当前对话上下文
   如果当前正在聊某个项目，默认归属该项目

4. 多匹配 → 列出候选项目（最多 3 个），让用户选

5. 完全无法判断 → 保留在 INBOX，不标记 ✅，等下次
```

---

## 写入目标

| 场景 | 写入位置 1 | 写入位置 2 |
|------|-----------|-----------|
| P0 / P1，归属明确 | 分项目 `system/current-state.md` → `## 当前任务` | `706-system/04-TASKS.md` |
| P2，归属明确 | 分项目 `system/current-state.md` → `## 当前任务` | — |
| 归属不明 | 保留在 INBOX，不操作 | — |

---

## 任务格式

写入分项目 `system/current-state.md`：

```markdown
- [ ] {任务描述} | P{0/1/2} | {deadline} | @{owner}
```

**Fallback**：如果分项目没有 `## 当前任务` section，按以下顺序找可用的 section 追加：
1. `## 下一步`（最常见）
2. `## 待办`
3. `## 待决策`
4. 都没有 → 在 `## 状态` 之后新建 `## 当前任务`

---

## 写入全局 04-TASKS.md

注意：04-TASKS.md 各优先级表格列数不同。

**P0 表（5 列）：**
```markdown
| {任务描述} | {项目简称} | {owner} | {deadline} | 🔴 待启动 |
```

**P1 表（4 列，无状态列）：**
```markdown
| {任务描述} | {项目简称} | {owner} | {deadline} |
```

**P2 表（2 列）：**
```markdown
| {任务描述} | {项目简称} |
```

---

## 确认格式

```
✅ {N} 条任务已分发
  → [{项目名}] {任务摘要}（P{0/1/2}）
  → [{项目名}] {任务摘要}（P{0/1/2}）
  → {M} 条保留在 INBOX（归属不明，待下次）
```

---

## 维护

- 新增项目时，更新 `references/project-routes.md` 的关键词。
- 路由逻辑变化时，更新本文件的路由决策树。
- Inbox Sync Protocol 变化时，更新本文件的协议原文。
