# Goal

## 场景

- 标题：{{TITLE}}
- 时长：{{MINUTES}} 分钟
- 模式：staged

## 完成条件

- `brief.md` 六格非空，purpose 与 takeaway 各一句。
- `architecture.md` 通过 Gate A（`check_architecture.py` 退出码 0）。
- `sections/*.md` 通过 Gate B（`check_moves.py` 退出码 0）。
- `script.md` 口播稿通过 Gate C：字数／时长在 ±10%、口述特征齐全、边界表完整。
- `delivery-notes.md` 有朗读实测。

## 约束

- 未经用户确认不改 brief 的 purpose 与 takeaway。
- 不用未核实数字；每条 evidence 带边界或显式标注 `[断言]`。
- 不在旧稿上直接改词：revision 模式先反推结构。
