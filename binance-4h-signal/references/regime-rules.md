# Regime Detection 与动态权重

## 什么是 Regime

市场不是匀质的。**趋势市**和**震荡市**对同一个指标的解读恰好相反:

| 信号 | 趋势市解读 | 震荡市解读 |
|---|---|---|
| RSI 70 超买 | 继续追多(动能强势) | 卖出(回归均值) |
| 价格触 BB 下轨 | 止损(跌势延续) | 买入(反弹) |
| MACD 金叉 | 强买入 | 可能诱多,等待确认 |

用同一套权重跑所有行情,会在两种市场里都有一半时间"做错"。Regime Detection 的意义是**先识别市场状态,再按状态切权重**。

## 当前识别规则(v2)

输入:滚动 4H 序列的 ADX、EMA20/50、BB Width 百分位(100 根窗口)。

```
if ADX > 25 and EMA20 > EMA50:       regime = trending_up
elif ADX > 25 and EMA20 < EMA50:     regime = trending_down
elif ADX < 20 and BBW_pctile < 30:   regime = ranging
else:                                regime = unknown  (按 ranging 应用权重)
```

### 为什么选这三个指标

- **ADX**:公认的趋势强度度量,>25 几乎必是趋势市,<20 几乎必是震荡市,20-25 是过渡带(归为 unknown)
- **EMA20/50 快慢方向**:在确认趋势市后,给出方向标签(up vs down)
- **BB Width 百分位**:ADX 本身会滞后,BB 挤压(百分位低)是震荡市的先行确认

### 阈值(可在 `config.regime` 调整)

| 参数 | 默认值 | 建议调参方向 |
|---|---|---|
| `adx_trend_th` | 25 | 趋势信号太少 → 调到 22;误报趋势 → 调到 28 |
| `adx_range_th` | 20 | 震荡太少 → 调到 22;误报震荡 → 调到 18 |
| `bbw_range_pctile` | 30 | 挤压过严 → 调到 40 |

## 权重矩阵

类别权重(每列合计 10,综合分尺度可比):

| 类别 | trending_up / down | ranging |
|---|---|---|
| trend | 3.0 | 1.0 |
| momentum | 2.0 | 1.5 |
| volatility | 1.0 | 2.5 |
| volume | 1.5 | 1.5 |
| microstructure | 1.5 | 2.0 |
| sentiment | 1.0 | 1.5 |

**趋势市逻辑**:趋势是主线,放大 trend(3.0) + momentum(2.0),抑制 volatility(1.0)。情绪和微观结构在趋势里作用有限,降权。

**震荡市逻辑**:价格在箱体内运动,volatility(2.5)——触边反弹概率高;microstructure(2.0)——极端资金费率常成为反转催化剂;trend(1.0)——弱方向性,降权。

## unknown 的处理

介于 trending 和 ranging 之间的状态(ADX 20-25,或 ADX>25 但 EMA 快慢差异不明显)。
保留 `unknown` 作为诊断标签,但应用权重时按 `ranging` 处理 —— 偏保守,不盲目押趋势。

## 可解释性

每次信号输出都带 `regime_diag`,示例:

```json
"regime": "trending_down",
"regime_diag": {"adx": 37.09, "bbw_pctile": 29.0, "atr_pctile": 34.0, "ema_fast_gt_slow": false}
```

这让人工审查时可以直接看到"为什么是 trending_down"——ADX 高达 37 且 EMA 快线低于慢线。

## 调参纪律

- **积累样本前不调**:至少 2880 条(4 币对 × 24h × 30 天)
- **分 regime 评估**:分别计算每个 regime 下的信号胜率(需要事后价格对比脚本)
- **失真信号**:某类别在某 regime 下胜率 < 45%,就把该 regime 下该类别的权重设为 0
- **不要过拟合单一币对**:权重在 4 个币对上应该都有合理表现,不能只为 BTC 调到最优

## 下一步可能的升级(非 Stage 2 范围)

1. **规模识别(volatility regime)**:低波动 / 高波动 / 过渡,进一步细分
2. **时间 regime**:亚洲盘 / 欧洲盘 / 美洲盘的权重微调
3. **机器学习替代**:用 XGBoost 直接学"市场状态 → 最优权重",前提是有足够标签数据和严格 out-of-sample 验证
