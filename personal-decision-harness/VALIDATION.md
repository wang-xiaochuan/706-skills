# v0.1 验证记录

日期：2026-09-08

## 已验证

- SKILL.md frontmatter 含名称与触发描述，正文少于 500 行。
- 使用说明、四份模板、底稿和两个虚构案例均存在。
- Codex 安装符号链接解析到当前权威源。
- data/ 为 0700，底稿为 0600；git check-ignore 确认底稿被排除。
- 真实决策与周计划目录为空，没有把测试或假想案例当成用户经历。

## 行为检查

两个独立代理分别进行有 skill 与无 skill 的两题模拟；输出及评审位于 ../personal-decision-harness-workspace/iteration-1/。两题各四项预设要求：有 skill 满足 8/8，无 skill 满足 6/8。差异主要是能力练习及确认状态；不代表判断正确率。主代理人工评审，未盲评或重复抽样。详见 [评审](../personal-decision-harness-workspace/iteration-1/REVIEW.md)。

## 限制

- 本机 skill-creator 安装只有流程文档，未找到其 generate_review.py、聚合和验证脚本。评审使用 Markdown 与 JSON 保存，不声称已经打开原版评审器。
- 未测试新会话自动触发率；本会话可通过读取 SKILL.md 使用。
- 这只是小样本流程检查，不是判断准确率、能力提升或长期结果验证。
- 没有虚构实际决策与回看结果，也没有修改用户全局记忆。
