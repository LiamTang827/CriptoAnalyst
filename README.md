# CriptoAnalyst — 多链加密货币 AML 风险溯源系统

基于交易图树状追踪的区块链地址风险识别工具，支持跨链追踪与自适应深度分析。

## 功能概述

- **多跳树状追踪**：以目标地址为根节点，BFS 递归展开关联地址，构建风险溯源树
- **五类节点分类**：`blacklisted` / `suspect` / `high_risk` / `bridge_dst` / `clean`
- **透明桥 vs 不透明桥**：区分可追踪桥（LayerZero、Rollup 官方桥）和不可追踪桥（Multichain、Synapse），后者等同混币器处理
- **跨链追踪**：解析桥合约事件日志（calldata + getLogs），切链后继续分析
- **自适应深度**：可疑分支自动获得额外追踪深度，平衡追踪覆盖率与算力成本
- **风险传播**：后序遍历，每跳 ×0.6 衰减，向上传播子树最高风险
- **Mermaid 可视化**：导出 `.md` 文件，可在 GitHub / Obsidian 直接渲染

## 文件结构

```
├── aml_analyzer.py           # 单地址 AML 分析引擎（Etherscan + TronScan + BridgeTracer）
├── trace_graph.py            # BFS 树状追踪引擎 + CLI 入口
├── cross_chain_tracer.py     # 跨链桥追踪：解析单笔桥 tx 的目标链和目标地址
│                             #   支持 Stargate / Orbiter / Across / Celer / Hop
├── bridge/
│   ├── bridge_event_scanner.py  # 桥事件批量扫描器（getLogs + indexed topic filter）
│   │                            #   解决 txlist 遇合约地址断链的问题
│   └── Etherscan_getlogs.py     # getLogs 工具脚本（Uniswap V3 池子示例）
├── dune_data.py              # Dune Analytics 数据拉取
├── dune_find_bridge_cases.py # 用 Dune 挖掘桥相关 AML 测试案例
├── Etherscan_txlist.py       # Etherscan txlist 工具脚本
├── find_test_cases.py        # 从黑名单地址挖掘测试案例
├── usdt_blacklist.csv        # USDT 黑名单（Tether 冻结地址，~8500 条）
├── .env.example              # 环境变量模板（API Key 配置）
├── TRACE_LOGIC.md            # 系统追踪逻辑详细文档
├── logic_diagrams.md         # 系统逻辑 Mermaid 图集（5 张）
└── midterm_report_background.md  # 项目中期报告背景与文献综述
```

## 快速开始

### 1. 安装依赖

```bash
pip install requests python-dotenv pandas
```

### 2. 配置 API Key

```bash
cp .env.example .env
```

然后编辑 `.env`，填入真实的 API Key：

```env
ETHERSCAN_API_KEY=your_etherscan_api_key_here
DUNE_API_KEY=your_dune_api_key_here
```

- **Etherscan API Key**：免费注册于 [etherscan.io/myapikey](https://etherscan.io/myapikey)，免费版限 5 req/s
- **Dune API Key**：免费注册于 [dune.com/settings/api](https://dune.com/settings/api)，仅 `dune_data.py` 和 `dune_find_bridge_cases.py` 需要

### 3. 运行追踪

```bash
# 快速筛查（约 30 秒）
python3 trace_graph.py 0xYourAddress --depth 2 --children 3 --nodes 10 --no-trace

# 标准分析（近 2 年交易）
python3 trace_graph.py 0xYourAddress --depth 3 --time-window 730

# 深度分析 + 导出 Mermaid 图
python3 trace_graph.py 0xYourAddress --depth 4 --nodes 60 --mermaid report.md --json report.json
```

### 完整参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--chain` | `ethereum` | 链类型：`ethereum` / `tron` |
| `--depth` | `3` | 最大追踪深度 |
| `--children` | `5` | 每节点最大子节点数 |
| `--nodes` | `50` | 全局节点上限 |
| `--depth-bonus` | `1` | 可疑分支额外深度 |
| `--time-window` | `0` | 只分析最近 N 天交易（0=不限） |
| `--mermaid FILE` | — | 导出 Mermaid 图 |
| `--json FILE` | — | 导出 JSON 结构 |
| `--no-trace` | — | 禁用跨链追踪 |

## 跨链追踪模块说明

### 问题背景

`txlist` API 只能查"某地址主动发起的交易"。当追踪链遇到**桥合约地址**时，合约没有主动发起 tx，txlist 返回空，追踪断链。

### 两种解法

| 模块 | 适用场景 | 方法 |
|------|----------|------|
| `cross_chain_tracer.py` | 已知单笔桥 tx hash | 解析 tx input calldata 或 tx receipt logs |
| `bridge/bridge_event_scanner.py` | 给定地址，批量扫描所有跨链事件 | getLogs + indexed topic filter |

### bridge_event_scanner.py 的核心原理

桥合约 emit 事件时，`sender/depositor` 通常是 `indexed` 参数，编码在 topic[1~3]。
Etherscan getLogs 支持按 topicN 过滤，因此可以直接查询：

> 合约 `0x5427...`（Celer）里，所有 `topic[2] = 发送方地址` 的 `Send` 事件

不依赖 txlist，对合约地址同样有效，也能捕获通过聚合器间接触发的跨链。

```bash
# 扫描某地址的所有跨链事件
python3 bridge/bridge_event_scanner.py 0xYourAddress

# 指定 block 范围（更快）
python3 bridge/bridge_event_scanner.py 0xYourAddress --from-block 18000000 --to-block 19500000

# 保存结果到 JSON
python3 bridge/bridge_event_scanner.py 0xYourAddress --output result.json
```

**支持的桥**：Celer cBridge v2 / Across Protocol v2+v3 / Stargate Finance / Wormhole

**注意**：Stargate 的 Pool Swap 事件不含目标地址（to），发现事件后需配合 `cross_chain_tracer.StargateTracer` 解析 tx calldata 获取。

## 相关文献

本系统的设计参考了以下工作：

- Möser et al. (2014) *Towards Risk Scoring of Bitcoin Transactions* — 多跳风险评分奠基论文
- Hercog & Povšea (2019) *Taint Analysis of the Bitcoin Network* — TaintRank 算法
- Liao et al. (2025) *Transaction Proximity* (Circle Research) — BFS 在 Ethereum 全图上的实践
- Mazorra et al. (2023) *Tracing Cross-chain Transactions between EVM-based Blockchains*
- Sun et al. (2025) *Track and Trace: Automatically Uncovering Cross-chain Transactions*

## 注意事项

- Etherscan 免费 API 有速率限制（5 req/s），分析大树时耗时较长
- `usdt_blacklist.csv` 数据来源于 Tether 官方公开冻结记录，不包含 OFAC 制裁名单
- 本工具仅供研究用途
