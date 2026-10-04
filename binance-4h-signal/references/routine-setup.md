# Claude Code Routine 配置指南

基于 [Anthropic 2026-04-14 发布](https://code.claude.com/docs/en/scheduled-tasks) 的 Claude Code Routines —— 云端跑,不依赖本机。

## 核心约束

- **最小粒度 1 小时**:cron 不能比 `0 * * * *` 更密
- **需要 git repo**:Routines 只能访问 project 里 `.claude/skills/` 下已 commit 的 skills
- **云端执行**:所以 skill 的所有依赖(`requests/pandas/numpy`)必须能通过 pip 自动安装

## 步骤 1:把当前 skills 目录变成 git repo

```bash
cd "$706_CLOUD/2026 skills"
git init
git add .
git commit -m "Initial skills collection"

# 推到私有 GitHub repo(推荐)
gh repo create my-claude-skills --private --source=. --push
```

## 步骤 2:把 skill 移到 Claude 识别路径

Claude Code Routines 读 `.claude/skills/<skill-name>/SKILL.md`。
当前 skill 路径是 `binance-4h-signal/SKILL.md`,需要软链或移入 `.claude/skills/`:

```bash
mkdir -p .claude/skills
ln -s "../../binance-4h-signal" .claude/skills/binance-4h-signal
# 或者直接 mv:
# mv binance-4h-signal .claude/skills/
```

## 步骤 3:在 Claude Code 里创建 Routine

在 Claude Code CLI 里执行:

```bash
/schedule create
```

交互式填写:
- **Name**: `binance-4h-signal-hourly`
- **Cron**: `5 * * * *`(每小时第 5 分钟 —— 避开整点拥堵)
- **Prompt**:
  ```
  运行 skill binance-4h-signal,调用 scripts/run.py 抓取 BTCUSDT/ETHUSDT/SOLUSDT 的
  最新 4H 滚动信号并追加到今日日志。如果是 UTC 日期首次运行,同时生成昨日日报。
  信号分 |score| > 6 时在回复开头用醒目标记高亮。
  ```
- **Repo**: 选你刚 push 的 repo

或者不用 CLI,手动在项目根写 `.claude/routines/binance-4h.yaml`:

```yaml
name: binance-4h-signal-hourly
schedule:
  cron: "5 * * * *"
  timezone: UTC
prompt: |
  运行 binance-4h-signal skill:
  1) 执行 python .claude/skills/binance-4h-signal/scripts/run.py
  2) 读取最新 logs/signals_$(date -u +%Y-%m-%d).json 末尾一次的结果
  3) 若 |score| > 6,在输出顶部加 🚨 强信号提示
  4) 汇报当前各币对 action + score + price
skills:
  - binance-4h-signal
```

## 步骤 4:验证

```bash
/schedule list           # 查看所有 routine
/schedule run binance-4h-signal-hourly   # 立即触发一次
/schedule logs binance-4h-signal-hourly  # 看执行历史
```

## 备选方案:本地 cron(不依赖 Claude Code Routine)

如果你只想在本机跑、不用云端:

```bash
crontab -e
# 加入:
5 * * * * cd "/path/to/2026 skills/binance-4h-signal" && /usr/bin/env python3 scripts/run.py >> logs/cron.log 2>&1
```

## 日报查看

每小时运行都会刷新 `logs/daily_YYYY-MM-DD.md`。
可以把日报软链到 Obsidian 金库:

```bash
ln -s "/path/to/logs/daily_$(date -u +%Y-%m-%d).md" /path/to/obsidian-vault/706-trading/
```

每日 UTC 23:55 可以再安排一个 Routine 专门生成完整日报并推送到 Notion / 邮箱 / 微信。
