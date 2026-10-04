---
name: harness-goal-runner
description: >
  设计本地 Claude/DeepSeek goal harness 工作环境。用户提到 "harness"、
  "goal harness"、"目标推进"、"自动跑 Claude"、"让 Claude 不停做"、
  "缠着 goal.md"、"runner"、"持续执行目标"、"自动检查直到完成" 时触发。
  这个 skill 用于把具体任务转成 goal.md + checks.sh + run.sh 的可落地结构，
  让 CLI agent 能围绕明确目标、验收命令、轮数和预算持续推进。
---

# Harness Goal Runner

## 你在做什么

帮用户把一个模糊的「让 Claude 一直做直到完成」需求，设计成一个本地 goal harness。

核心解释：

```text
goal.md   = 目标说明书，记录要完成什么
checks.sh = 验收脚本，判断是否完成
run.sh    = 外层 runner，反复调用 claude 并运行 checks
```

不要暗示 `goal.md` 自己会自动执行。自动推进来自 runner。

## 工作流

### Step 1: 判断任务类型

先判断用户要推进的任务属于哪类：

- 代码任务：修 bug、跑测试、整理项目、生成脚手架
- 知识库任务：迁移文件、整理目录、生成索引、检查重复
- 内容任务：长文、推文、报告、讲稿、多轮打磨
- 数据任务：表格清洗、文件批处理、批量转写
- 运维任务：检查服务、同步配置、验证环境

如果任务会修改真实文件，必须把允许修改的目录写入 `goal.md`。

### Step 2: 收集最少必要信息

从用户上下文和当前工作区推断，缺关键项再问。需要锁定：

- `workspace`: harness 放在哪里
- `target_cwd`: Claude 执行任务的工作目录
- `objective`: 最终目标
- `constraints`: 不能做什么
- `done_when`: 人类可读的完成标准
- `check_commands`: 机器可执行的检查命令
- `max_turns`: 默认 5
- `max_budget_usd`: 默认 2

706 工作区默认约束：

- 不要在 `706-knowledge` 中执行 `git init`、`git add`、`git commit`、`git gc`、`git repack`。
- 对 OneDrive 同步区的迁移/整理任务，优先用 `find`、`diff -qr`、`rsync --dry-run`、文件清单和时间戳验证。

### Step 3: 设计 harness 目录

输出或创建如下结构：

```text
<workspace>/
  goal.md
  checks.sh
  run.sh
  logs/
```

默认不要创建无限循环。`run.sh` 必须有最大轮数；预算通过 Claude CLI 的 `--max-budget-usd` 控制。

### Step 4: 生成三个文件

优先复用本 skill 的模板：

- `templates/goal.md`
- `templates/checks.sh`
- `templates/run.sh`

按具体任务替换占位内容。`checks.sh` 可以先从最小可验证命令开始，例如：

- 代码任务：`npm test`、`npm run build`、`pytest`
- 知识库任务：`test -f`、`find ... | wc -l`、`diff -qr`
- 内容任务：检查目标文件存在、标题/章节存在、字数下限
- 数据任务：检查输出文件存在、行数、字段名

### Step 5: 告诉用户如何运行

给出明确命令：

```bash
cd "<workspace>"
bash run.sh
```

同时说明：

- 第一轮会把 `goal.md` 喂给 Claude。
- 每轮结束会运行 `checks.sh`。
- 检查失败时，runner 会把失败信息发给 `claude --continue`。
- 检查通过、达到最大轮数、或 Claude 调用失败时停止。

## Runner 设计要求

`run.sh` 应该：

- 使用 `set -u`，但不要用容易吞掉诊断信息的复杂 shell 技巧。
- 每轮写入 `logs/turn-N.txt` 和 `logs/check-N.txt`。
- 第一轮用 `claude -p`，后续用 `claude --continue -p`。
- 把 check 失败输出压缩进下一轮 prompt。
- 暴露 `MAX_TURNS`、`MAX_BUDGET_USD`、`PERMISSION_MODE` 环境变量。
- 默认 `PERMISSION_MODE=acceptEdits`，需要全自动高权限时让用户显式改。

## 输出格式

如果用户只是询问方案，输出：

~~~markdown
## Harness 结构
...

## goal.md
```markdown
...
```

## checks.sh
```bash
...
```

## run.sh
```bash
...
```

## 运行方式
...
~~~

如果用户要求实现，并且当前模式允许写文件，就实际创建文件，然后汇报路径和验证结果。

## 失败处理

- 如果没有可执行验收标准，不要伪造复杂检查；先用文件存在、构建命令、测试命令或清单检查做最小验收。
- 如果 Claude CLI 不存在，先让用户安装或确认命令名，不要改用别的模型 API。
- 如果任务需要长期无人值守，建议升级到 Node runner；第一版 shell runner 适合个人端短任务。
