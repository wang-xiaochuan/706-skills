# 09-video-production 员工契约

仅在由数字员工执行或需要跨员工 handoff 时读取。

## 状态机

`inbox → current-task → analysis → EDL → roughcut → style sample → batch render → QA → outputs → handoff/report → done`

每一步都要能从文件恢复：

| 阶段 | 最小恢复文件 |
|---|---|
| analysis | source register、媒体 probe、转录状态 |
| EDL | 机器可读 EDL、版本矩阵、待确认项 |
| roughcut | resolved EDL、粗剪路径、抽帧联系表 |
| style sample | 字幕/标题/姓名/封面样片与用户反馈 |
| batch render | manifest、已完成输出列表、失败重试记录 |
| QA | ffprobe、完整解码、首中尾/边界抽帧 |
| handoff | 上传说明、目标员工、发布边界 |

## 归属与 handoff

- 09 是视频成品、字幕、封面和 QA 的 owner。
- 项目目录是产物容器；员工 `outputs/INDEX.md` 记录归属和真实路径。
- 综合传播包装交给 02-media。
- 可上传包交给 05-outreach；09 不登录平台或直接发布。
- 可复用语料和方法沉淀交给 06-knowledge。
- 通用 Skill 与脚本升级请求交给 07-dev。

## 三个人工门

1. 发布门：权限、敏感内容、目标平台。
2. 编辑门：说话人、删除边界、完整叙事结构。
3. 视觉门：第一条样片的镜头、标题、字幕、姓名和封面。

除这些门以外，员工应通过现有证据和保守默认值继续推进，不把每个小判断都升级给用户。

## 任务完成

完成时：

1. 更新员工 `outputs/INDEX.md`。
2. 在 `log.md` 记录产出、耗时、QA 和遗留风险。
3. 写 report 给 01；需要分发时写 handoff 给 05。
4. task frontmatter 标记 `done`，加入 `closed` 与 `closed-by: 09`。
5. task 移入 `done/`，不删除。
