# 口述修辞结构 Harness · 项目模板

这是 `rhetorical-structure-harness` 的实例骨架。控制面是文本，脚本只读注释标记内的内容。

## 门禁顺序

```text
brief.md            → Gate 0
architecture.md     → Gate A   (Layer 1)
sections/NN-*.md    → Gate B   (Layer 2)
script.md           → Gate C
delivery-notes.md   → Gate D
```

## 命令

```bash
python3 <skill>/scripts/check_architecture.py .
python3 <skill>/scripts/check_moves.py .
```

`state.csv` 进行中恰好一个 `ACTIVE`；上游未通过不得创建下游正式产出。
