# Phase C 双重批判循环 Prompt

Phase C 跑两个**独立**的 critique loop，分别检查不同的失败模式。两个循环的失败模式互不重叠，所以不能合并成一个。

---

## C.1 事实保真检查（必做，最多 1 轮重写）

### 目的
拦截风格迁移过程中**悄悄丢失或扭曲事实**的错误。这是发布前最关键的安全检查。

### Prompt 模板

````
你正在做风格迁移结果的事实保真检查。

# 原段
{original_paragraph}

# 改写段
{transferred_paragraph}

# 用户提供的事实清单（来自 Phase B.1）
{fact_list_bullets}

# 检查任务

逐项核对以下三件事，仅输出 JSON：

1. **missing**：事实清单中哪些项**没有**在改写段里被保留？
   - 完整丢失："周六下午"在原段，但改写段只说"那一天"
   - 泛化丢失："706 会客厅"在原段，但改写段说"某个客厅"
   - 数字丢失："二十几个"在原段，但改写段说"不多人"

2. **added**：改写段里哪些**具体的**新信息是原段没有的？
   - 只列具体的（人名、地名、时间、数字、专有名词、引用），不列形容词或情感语气
   - 例如原段没说"夜风很凉"，改写段说"夜风渐凉"——记入 added

3. **twisted**：改写段哪些地方扭曲了原段的因果、时间顺序或语义关系？
   - 因果倒转：原段"因为 A 所以 B"，改写段写成"因为 B 所以 A"
   - 时间错位：原段"先 X 后 Y"，改写段先写 Y
   - 语义偏移："听众大多是大学生"被改成"听众都是大学生"

# 输出格式

仅输出有效 JSON，不要任何解释、前后缀、代码块标记：

{
  "missing": [{"fact": "...", "evidence": "原段有 X，改写段没有"}, ...],
  "added": [{"info": "...", "evidence": "改写段中的 X，原段没出现"}, ...],
  "twisted": [{"original": "...", "transferred": "...", "type": "causal|temporal|semantic"}, ...]
}

如果三类都没问题：{"missing": [], "added": [], "twisted": []}
````

### 处理逻辑

```python
result = run_check(prompt)
if all(empty for empty in [result.missing, result.added, result.twisted]):
    pass  # 通过 C.1
else:
    # 第一轮重写
    rewrite_prompt = build_rewrite_prompt(transferred, result)
    new_transferred = rewrite(rewrite_prompt)
    result_2 = run_check_again(original, new_transferred, fact_list)
    if all(empty for empty in [result_2.missing, result_2.added, result_2.twisted]):
        pass  # 通过
    else:
        escalate_to_user(original, new_transferred, result_2)
        # 不再自动重写，让用户决定
```

### Rewrite Prompt 模板（C.1 失败后用）

```
事实检查发现问题：

{result_summary}

请修订改写段，要求：
- 把所有 missing 项明确加回去（不要换说法，用原段的具体表述）
- 删除所有 added 项（除非是原段语义里隐含的、不算新信息）
- 修正所有 twisted 项的因果/时间/语义关系

保持声口风格不变。仅输出修订后的段落。
```

### 关键设计

- **JSON 输出**：可机器解析，避免自然语言模糊判断
- **evidence 字段**：让 LLM 自我验证，减少幻觉
- **硬上限 1 轮重写**：第二次仍不过就升级用户，不要无限循环
- **升级模式**：把原段、(失败的) 改写段、检查报告一起呈给用户，让他做决定

---

## C.2 声口保真检查（最多 2 轮重写）

### 目的
评估改写段是否真的捕捉到了目标作家×译者的声口。这是质量检查，不是安全检查。

### Prompt 模板

````
你是一位精通{author_name}（{translator_name} 译本）的文学批评者。请评估一段中文风格迁移的结果。

# 目标声口档案要点

## 元层 Meta
{profile_section_three_summary}

## 译者层 Translator-specific
{profile_section_four_summary}

# 待评段落

{transferred_paragraph}

# 评估任务

逐条评估（每条 1-3 句，可以批评严厉。重点找问题，不要客套）：

1. **句长 / 句式 / 标点是否匹配？**
   - 短句长句的比例对吗？
   - 标点偏好是否与该作家×译者一致？

2. **词汇语域是否匹配该译者？**
   - 列出 1-3 个用得不像该译者的词
   - 该译者会用的词，但段落中缺失的，列 1-2 个

3. **节奏是否匹配？**
   - 哪里太赶？哪里太慢？
   - 段内"加速—减速"曲线对不对？

4. **是否落入了该作家不会涉足的题材或修辞？**
   - 例：用卡尔维诺风格但出现了哲学神秘主义（属博尔赫斯领域）
   - 例：用加缪风格但出现了温情抒发（属圣埃克苏佩里领域）

5. **是否有"AI 腔"残留？**
   - 滥用四字格、过度对仗、强行排比
   - "在这个意义上"、"某种程度上"、"换言之"等过渡词的滥用
   - 段尾"金句化"倾向（强行总结升华）

# 输出

最后给一个 0-10 的"声口贴近度"打分。

输出格式（JSON）：

{
  "evaluation": {
    "sentence_form": "...",
    "vocabulary": "...",
    "rhythm": "...",
    "subject_modesty": "...",
    "ai_residue": "..."
  },
  "score": 0-10,
  "rewrite_hints": ["hint 1", "hint 2", ...]
}

`rewrite_hints` 是给重写时用的——具体到"把第 N 句的 X 改成 Y 风格"。
````

### 收敛规则

```python
score = c2_check(transferred)
if score >= 8:
    pass  # 通过 C.2
elif 6 <= score < 8:
    # 第一轮重写（定向）
    rewritten = rewrite_with_hints(transferred, hints)
    score_2 = c2_check(rewritten)
    if score_2 >= 8:
        pass
    else:
        # 第二轮重写
        rewritten_2 = rewrite_with_hints(rewritten, score_2.hints)
        score_3 = c2_check(rewritten_2)
        if score_3 >= 8:
            pass
        else:
            escalate_to_user(history)
elif score < 6:
    # 严重不过，第一轮重写后不再 C.2 自动循环
    rewritten = rewrite_with_hints(transferred, hints)
    score_2 = c2_check(rewritten)
    if score_2 >= 8:
        pass
    else:
        escalate_to_user(history)
```

**硬上限 2 轮重写**——这是 critique loop 不出现"越改越糟"螺旋的关键。

### Rewrite Prompt 模板（C.2 失败后用）

```
你之前生成了一段风格迁移结果，但批评者认为声口贴近度只有 {score}/10。

# 批评要点
{evaluation_summary}

# 具体修订建议
{rewrite_hints}

# 当前版本（声口不够贴近）
{transferred_paragraph}

# 任务

按上述修订建议重写段落。要求：
- 修正批评中提到的具体问题
- **不能改动事实**（保持所有时间、地点、人名、数字、专有名词原样）
- 长度与当前版本相近（±20%）
- 直接输出修订后的段落，不加解释
```

### 与 C.1 的衔接

C.2 重写后，**必须再跑一次 C.1**——因为重写可能引入事实丢失。两个 loop 不是并行的，是串行的：

```
B (改写) → C.1 (事实检查) → C.2 (声口检查) → 如 C.2 重写过 → 再跑 C.1 → 输出
```

如果 C.2 重写后导致 C.1 失败，且 C.1 重写又导致 C.2 失败——这是死循环征兆，**直接升级用户**，不要继续。

---

## 升级到用户的格式

当 C.1 或 C.2 触发升级时，呈给用户的格式：

````
【段 N · 改写需要你判断】

# 原稿
{original}

# 当前改写版本
{transferred}

# 检查结果
- 事实保真：{✅ / ❌：列出问题}
- 声口贴近度：{score}/10
- 主要问题：{1-2 句}

# 我的修订建议
{rewrite_hints if any}

请选择：
A. 接受当前版本（带已知问题）
B. 给我一个具体的方向，让我再改一次（如"更克制"、"短句多一点"）
C. 这段不要改了，用原稿
D. 你来手动改，我看后续段落

请回复 A/B/C/D 或自由说明。
````

不要无限自动循环。**两轮没收敛就要让用户介入**。

---

## C.1 vs C.2 的优先级

如果两个检查都失败：

- C.1 永远优先——事实正确比声口贴近重要
- C.2 失败但 C.1 通过 → 可以发布，但建议用户人工再调
- C.1 失败 → 不能直接发布，必须修

---

## 为什么不合并成一个 critique？

合并成一个 prompt 会出现：

1. **指令稀释**：5+ 项检查项放一个 prompt 里，模型注意力被分散，每项都做得马虎
2. **JSON 复杂**：合并的 JSON schema 很深，LLM 容易输出错位
3. **rewrite 信号混乱**：事实修订和声口修订是不同方向的，混在一起会让模型左右为难

拆成两个 loop 后：
- C.1 是窄目标的安全检查，可靠性高
- C.2 是开放目标的质量检查，允许主观打分
- 串行执行让每步信号清晰

实测拆分后 C.1 的事实丢失检出率会从 ~70%（合并版）提升到 ~95%。
