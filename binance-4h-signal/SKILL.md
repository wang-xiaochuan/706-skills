---
name: binance-4h-signal
description: 从 Binance 公开 API 抓取 1H K 线滚动合成 4H,融合 23 个指标(趋势/动能/波动/量价/微观结构/情绪),按市场 regime 动态切换权重矩阵,输出买卖建议并追加到本地日志以支持跨次对比。当用户说「跑一下 4H 信号」「看看 BTC 4小时级别」「现在的交易建议」「和上次比怎么样」「最近走势」「crypto signal」「跑交易模型」「对比一下」「Binance 信号」,立刻触发。如果用户问"和上次比",用 --compare 参数。
type: trading-signal
---

# Binance 4H 短期信号(1H 滚动合成 + Regime 切换)

## 两个核心思想

### 1. 滚动 4H 合成 —— 信号刷新快 4 倍

传统 4H K 线每 4 小时才定型一次,信号滞后。本 skill 每小时取**最近 4 根 1H K 线**合成一根"滚动 4H"(open=T-3h 开盘,high/low 取 4 根极值,close=当前 1H 收盘,volume 求和),让 4H 级别指标每小时都能更新。

### 2. Regime Detection —— 按市场状态切权重

趋势市和震荡市对同一个指标的解读相反(例:触 BB 下轨在趋势市是止损信号,在震荡市是买入信号)。本 skill 识别三档 regime:

- **trending_up / trending_down**: ADX>25 + EMA 快慢方向
- **ranging**: ADX<20 且 BB 带宽百分位<30
- **unknown**: 介于之间,按 ranging 权重处理

不同 regime 下 6 大类指标(trend / momentum / volatility / volume / microstructure / sentiment)权重比例不同,让信号更贴近市场本质。详见 [references/regime-rules.md](references/regime-rules.md)。

## 23 个指标(6 大类)

| 类别 | 指标 |
|---|---|
| **trend** (4) | EMA20/50 Cross · EMA200 Position · ADX(14) · HTF Alignment (1D EMA50 方向) |
| **momentum** (4) | MACD(12,26,9) · RSI(14) · Stoch RSI · ROC(10) |
| **volatility** (4) | Bollinger %B · BB Width 百分位 · ATR% 百分位 · Keltner Squeeze |
| **volume** (3) | Volume vs MA20 · OBV Trend · Taker Buy Ratio |
| **microstructure** (4) | Funding Rate · OI 24h 变化 · Perp-Spot Basis · 清算脉冲(stub) |
| **sentiment** (4) | Top Trader L/S · Retail L/S · Fear & Greed · 智能钱-散户背离 |

每个指标独立评分到 [-2, +2] → 类别内等权平均到类别分 → 类别分乘 regime 权重 → 加总为综合分 → 阈值映射到 Action。

## 使用场景

1. **一次性查询**:用户问「现在 BTC 4H 信号如何」→ `python3 scripts/run.py --symbols BTCUSDT`
2. **Routine 模式**(推荐):部署为 Claude Code Routine,每小时第 5 分钟自动跑一次,累积信号日志,附带中文分析 + 强信号告警

## 流程

1. **抓 K 线**:`/api/v3/klines` 拉 240 根 1H + 60 根 1D(缓存 2h)
2. **拉 meta**(并发,含 sqlite 缓存):funding / OI / basis / top_ls / retail_ls + 共享 F&G
3. **滚动 4H 合成** + `compute_all` 算 23 个指标的 series 列
4. **aggregate_scores** 合成 6 个类别分 + 23 个子项分 + 每项状态
5. **regime.detect** 决定市场状态
6. **signal_engine.generate**:按 regime 权重加权,输出 Signal(带 SL/TP)
7. 写入 `logs/signals_YYYY-MM-DD.json`,刷新 `logs/daily_YYYY-MM-DD.md`

## 运行方式

```bash
# 手动一次(默认 BTCUSDT ETHUSDT SOLUSDT BNBUSDT)
python3 scripts/run.py

# 指定币对
python3 scripts/run.py --symbols BTCUSDT,ETHUSDT

# 跑一次 + 和最近 5 次历史横向对比(推荐,用户手动驱动观察时最好用)
python3 scripts/run.py --compare 5

# 不跑,只读历史对比(比如当天没网,想复盘)
python3 scripts/run.py --compare-only 10

# 只生成日报(读当天已跑的 JSON)
python3 scripts/run.py --daily-only

# 开关某个指标(修改 config.features_enabled 字典)
# 比如关掉 F&G:"fear_greed": false
```

### 用户手动触发模式(推荐)

这个 skill 的主要工作方式是**用户在 Claude Code 里说一句话就触发**,不需要定时任务:

- 用户说「跑一下信号」「看看现在 BTC 如何」→ 跑 `scripts/run.py`
- 用户说「和上次比怎么样」「最近走势」→ 跑 `scripts/run.py --compare 5`
- 用户说「今天的日报」→ 跑 `scripts/run.py --daily-only`

每次跑都会把完整结果追加到 `logs/signals_YYYY-MM-DD.json`,自动形成历史序列,为跨次对比提供数据。**用户想观察多久就跑多久,想在哪个时点采样就在哪采样**,不强制固定频率。

## 输出示例(简化)

```
[BTCUSDT] SELL        score=-3.08  regime=trending_down  T-0.50 M+0.00 V+0.12 Vol-1.17 Mi+0.00 S+0.05  price=74722.9
```

其中 T/M/V/Vol/Mi/S 分别是 trend/momentum/volatility/volume/microstructure/sentiment 类别分。

JSON 输出含 `regime`、`regime_diag`、`category_scores`(6 项)、`components`(23 项平铺) 、`components_status`(每项 ok/cached/disabled/missing/error)、`meta`(原始数值)、`indicators`(TA 数值)、`stop_loss`/`take_profit`。

## Routine 部署

参见 [references/routine-setup.md](references/routine-setup.md)。核心:`.claude/routines/binance-4h-test.yaml`,cron 设为 `5 * * * *`。

## 依赖

- Python 3.10+
- `requests`、`pandas`、`numpy`
- 不依赖 TA-Lib(纯 pandas 实现)

## 文件结构

```
binance-4h-signal/
├── SKILL.md
├── config.json                    # 币对、features_enabled、weights_by_regime、cache TTL
├── requirements.txt
├── scripts/
│   ├── run.py                     # 主入口
│   ├── cache.py                   # sqlite KV + TTL
│   ├── regime.py                  # regime 识别 + 权重解析
│   ├── signal_engine.py           # 综合评分 + Signal 输出
│   ├── fetchers/
│   │   ├── _http.py               # 带重试的 HTTP GET
│   │   ├── klines.py              # 1H + 1D K 线 + 滚动 4H 合成
│   │   ├── futures_meta.py        # funding/OI/basis/liq
│   │   ├── sentiment_ls.py        # top/retail L/S
│   │   └── external.py            # Fear & Greed
│   └── indicators/
│       ├── _base.py               # ema/sma/rsi/atr/true_range/percentile 原语
│       ├── trend.py               # EMA cross / EMA200 / ADX / HTF
│       ├── momentum.py            # MACD / RSI / StochRSI / ROC
│       ├── volatility.py          # BB %B / BB Width / ATR% / Keltner
│       ├── volume.py              # Volume / OBV / Taker Ratio
│       ├── microstructure.py      # 评分:funding/OI/basis/liq
│       └── sentiment.py           # 评分:top_ls/retail_ls/F&G/divergence
├── references/
│   ├── strategy.md                # 策略设计总览
│   ├── regime-rules.md            # Regime 识别与权重详解
│   └── routine-setup.md           # Claude Code Routine 配置
└── logs/
    ├── cache.sqlite
    ├── signals_YYYY-MM-DD.json
    └── daily_YYYY-MM-DD.md
```

## 重要声明

本 skill 仅提供**技术分析信号**,不构成投资建议。加密货币波动剧烈,所有交易决策请结合基本面、风控和自身判断。信号系统未经正式回测,处于测试版阶段,权重和阈值可能需要根据实盘数据调整(建议样本量 ≥ 2880 条后再调权重)。
