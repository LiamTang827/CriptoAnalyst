# CriptoAnalyst — 多链加密货币 AML 风险溯源系统

基于交易图树状追踪的区块链地址风险识别工具，支持跨链追踪与自适应深度分析。

## 功能概述

- **多跳树状追踪**：以目标地址为根节点，BFS 递归展开关联地址，构建风险溯源树
- **五类节点分类**：`blacklisted` / `suspect` / `high_risk` / `bridge_dst` / `clean`
- **透明桥 vs 不透明桥**：区分可追踪桥（LayerZero、Rollup 官方桥）和不可追踪桥（Multichain、Synapse），后者等同混币器处理
- **跨链追踪**：通过 LayerZero Scan API 解析对端地址，切链后继续分析
- **自适应深度**：可疑分支自动获得额外追踪深度，平衡追踪覆盖率与算力成本
- **风险传播**：后序遍历，每跳 ×0.6 衰减，向上传播子树最高风险
- **Mermaid 可视化**：导出 `.md` 文件，可在 GitHub / Obsidian 直接渲染

## 文件结构

```
aml_analyzer.py          # 单地址 AML 分析引擎（Etherscan + TronScan + BridgeTracer）
trace_graph.py           # BFS 树状追踪引擎 + CLI 入口
cross_chain_tracer.py    # 跨链追踪辅助模块
usdt_blacklist.csv       # USDT 黑名单（Tether 冻结地址，~8500 条）
TRACE_LOGIC.md           # 系统追踪逻辑详细文档
logic_diagrams.md        # 系统逻辑 Mermaid 图集（5 张）
midterm_report_background.md  # 项目中期报告背景与文献综述
```

## 快速开始

### 安装依赖

```bash
pip install requests
```

### 配置 API Key

在 `aml_analyzer.py` 顶部填入你的 Etherscan API Key：

```python
ETHERSCAN_API_KEY = "your_key_here"
```

### 运行追踪

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
