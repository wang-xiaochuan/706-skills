# resume-hr-review

接入一个职位/JD 和一份上传简历，再模拟招聘初筛 HR 做逐项要求—证据对比。当前范围仅限 review：生成岗位画像、透明覆盖度、硬门槛状态、claim 可信度、ATS 风险与修改优先级；默认不改稿、不模拟面试、不执行投递。

## 状态

- `v0.2-draft`
- 已建立 `SKILL.md`、岗位画像模板、匹配规则、审查量表和 3 个测试用例。
- 当前主路径是单职位 × 单简历；批量候选人排名不在本版范围。
- 尚未完成 with-skill / baseline 对照测试，也未安装到运行时。

## 事实源

源目录是本目录。需要安装时使用：

```bash
$706_LOCAL/706-skills/infra/scripts/sync-skills.sh install resume-hr-review --runtime=codex
```

安装后需要新建 Codex 会话，当前会话不会热加载新 Skill。
