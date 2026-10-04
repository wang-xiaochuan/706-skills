# 证据模型与结构化研究门禁

## 1. 来源类型

| source_type | 能证明什么 | 不能自动证明什么 |
|---|---|---|
| `primary_record` | 合同、账目、档案、会议原件中明确记录的事实 | 记录之外的动机和普遍效果 |
| `law_or_official_text` | 文本发布主体、日期、适用范围和规范内容 | 实际执行效果；新闻作者的延伸解释 |
| `official_or_project_self_description` | 机构怎样描述项目、规模、目标、招募与计划 | 独立效果、代表性、长期存续和参与者体验 |
| `independent_report` | 记者可观察事实、具名访问与当时状态 | 未采访群体、全国普遍性和法律裁决 |
| `peer_reviewed_research` | 研究设计直接覆盖的样本与分析 | 样本外总体、后来状态或研究未测量的结果 |
| `directory_or_aggregator` | 候选发现、名称、入口线索 | 真实性、当前运营、规模和独立来源数量 |
| `oral_history` | 说话者的记忆、措辞、感受与线索 | 未经档案复核的年份、产权、城市总体史 |
| `cultural_work` | 时代感受、文化脚本和叙事想象 | 真实住房事实、人口数量或政策过程 |
| `author_inference` | 基于已列证据的透明分析 | 来源本身的结论或机构正式立场 |

## 2. 证据等级

- **A**：原始记录、法律原文、统计原表、同行评审研究或可重复数据。
- **B**：可追踪的官方／项目原页、具名深度报道、正式报告。
- **C**：聚合目录、单一索引、营销转载、缺少正文的元数据。
- **D**：未核口述或二手线索，只进入待核池。

等级不是可信度万能分数。A 级来源也只能支持其实际记录的范围；项目合同不能证明社区幸福，统计公报不能证明某个项目仍营业。

## 3. source-register 最小字段

```csv
source_id,title,source_type,evidence_grade,publisher_or_speaker,published_at,url_or_path,accessed_at,language,geographic_scope,can_support,cannot_support,archive_path,sha256,notes
```

要求：

- `source_id` 稳定且唯一，不因脚注重排而改变。
- 原 URL 与本地快照分开。
- `can_support` 使用具体对象和动词，不写“项目背景”。
- `cannot_support` 主动限制代表性、因果、现状或规模。
- 同文转载不因域名不同成为独立证据。

## 4. claim-evidence-register 最小字段

```csv
claim_id,chapter_or_output,claim_text,claim_type,risk_level,source_ids,evidence_relation,status,boundary_note,last_checked_at
```

`claim_type` 建议：`fact / number / quote / causality / law / current_status / scale / interpretation`。

`evidence_relation` 建议：

- `direct`：来源直接记录该事实。
- `triangulated`：两个真正独立来源支持同一事实。
- `self_description`：只写为机构自述。
- `oral_memory`：只写为回忆或线索。
- `inference`：作者明确推论。
- `insufficient`：不能进入确定句。

## 5. case-register 最小字段

```csv
case_id,name,location,object_type,status,inclusion_tier,brief_intro,latest_public_trace,preferred_link,source_ids,scale_value,scale_unit,scale_scope,population,governance,property_control,entry_path,exit_path,unknowns,last_checked_at
```

### 建模规则

- 一条记录对应一个明确单位：物理节点、组织版本、政策计划或短期实验需预先选择一种。
- 同品牌不同地点通常分行；同地点仅改名可用 lineage 字段关联。
- `planned`、`recruiting`、`active`、`historical`、`status_unverified` 不混写。
- 规模同时写数值、单位和作用域；房间、床位、容量、管理规模和实际入住分开。
- 项目链接优先原站；找不到原站时保留公开提及证据并明确 `not_found_in_this_search`。

## 6. coverage-matrix 最小字段

```csv
coverage_id,dimension,unit,query_set,platform_or_database,searched_at,result_count,retained_ids,no_result_note,next_action,status
```

`no_result_note` 不能留空。它说明执行了什么检索、为何没有可纳入结果；不能写成当地不存在。

## 7. unknowns 与 removal log

### unknowns.csv

```csv
unknown_id,object_id,question,why_it_matters,current_clues,needed_evidence,public_wording,status
```

未知项在正文可以写成：

- “现有材料尚不能确认……”
- “公开页面只显示……，没有提供……”
- “这是作者据此提出的研究问题，而不是已证实结论。”

不要把每个未知项都写成相同的警告句；根据其叙事位置表达。

### removal-log.csv

```csv
record_id,original_name,disposition,merged_into,reason,evidence_checked,decided_at
```

删除不是让候选消失。每条旧候选获得保留、合并、排除或线索处置，防止下一轮重复发明。

## 8. 法律、政策与智库分层

至少区分：

1. 法律／行政法规／司法解释。
2. 部门规章与地方政府规章。
3. 规范性文件、规划、试点和政策说明。
4. 政府网站刊载的研究者文章。
5. 党校、智库、媒体作者的署名观点。
6. 新闻解读。
7. 本文推论。

“发布在某机构网站”不等于“该机构正式预测”；“政策提出目标”不等于个人获得可诉权利。

## 9. 口述史处理

- 保存原始音频／转录、说话者匿名规则和访谈日期。
- 把可核事实拆成查档问题：地址、年代、产权、租约、行政机构、家庭人数。
- 叙事中可保留说话者的感受和措辞，但用“回忆”“据其讲述”标明位置。
- 与档案冲突时并列呈现，不用模型替双方和解。

## 10. 数字与计数门禁

每个数字回答：

- 时间点是什么？
- 地理范围是什么？
- 单位是什么？
- 分母是什么？
- 是计划、容量、管理量、开业量还是实际量？
- 是否与另一张表重叠？

常见禁止相加：

- 项目目录 + 节点谱系。
- 聚合报告总数 + 逐项目录。
- 品牌管理房间 + 单项目房间。
- 活动参与者 + 常住居民。
- 计划床位 + 已入住人数。

## 11. 研究自动审计建议

至少机器检查：

- CSV schema、必填字段、ID 唯一性、受控词汇。
- URL 格式和本地 archive 路径。
- source ID 跨表引用完整性。
- 每个 retained 案例至少一条公开提及证据。
- 旧候选均有 disposition。
- coverage 单元无空白。
- 不同地理口径分别统计。
- unknown 字段保留，不被空字符串吞掉。

自动通过不等于事实为真；它证明研究链没有结构性断裂。高风险主张仍需人工阅读原文。
