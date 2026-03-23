# 基于跨链追踪的加密货币反洗钱风险识别系统
## 中期报告

---

## 一、研究背景

### 1.1 加密货币洗钱问题的规模与演变

区块链的去中心化、假名性（pseudonymity）和全球可达性使其在带来金融创新的同时，也成为非法资金流动的重要渠道。Chainalysis 发布的 *2024 Crypto Money Laundering Report* 显示，2023 年非法加密货币地址共接收约 **409 亿美元**资金，而这一数字在 2025 年已增长至超过 **1,540 亿美元**，年增幅高达 162%。尤为值得关注的是，稳定币（Stablecoin）在非法交易中的占比已从早期的少数上升至 **63%**（2025 年更达 84%），犯罪分子正加速从比特币转向以 USDT 为代表的稳定币——原因正是其流动性强、跨链转移便捷，而监管盲区相对更大。

从犯罪类型来看，洗钱手段已呈现出系统性的"专业化"趋势。以 Huione Group 为例，该平台自 2021 年至今经手的加密货币交易额超过 **700 亿美元**，逐渐演化为一个服务于诈骗、洗钱全流程的地下金融基础设施。这一趋势表明，加密货币犯罪不再是分散的个人行为，而是具备组织结构和技术门槛的有组织犯罪。

### 1.2 跨链桥的崛起与监管盲区

近年来，跨链桥（Cross-chain Bridge）的规模急剧扩张。以 Stargate Finance 为例，其月均跨链交易量超过 **23 亿美元**，整个 DeFi 生态中每月跨链资产规模逾 **80 亿美元**。跨链桥的核心功能是允许用户在不同区块链之间转移资产，其本身是合法且重要的基础设施——但这一特性同样被犯罪分子系统性地利用于切断资金追踪链条。

Elliptic 于 2023 年的报告指出，**70 亿美元**的非法资产已通过跨链服务完成洗钱，且这一数字自 2022 年起持续快速增长。在可识别的洗钱方案中，**58% 使用了跨链桥**作为关键一环（2024 年数据）。Chainalysis 也在其 2024 年报告中指出，来自被盗资金关联地址的跨链桥使用量在 2023 年出现了大幅跃升。

以北韩黑客组织 Lazarus Group 的操作为例：
- **Ronin Bridge 攻击（2022 年 3 月）**：盗取约 6.25 亿美元，随后通过 Tornado Cash 混币、Avalanche 跨链桥切链到比特币网络，再经 Sinbad 混币器二次清洗，整个洗钱流程横跨超过 12,000 个地址、涉及多条链。
- **Harmony Horizon Bridge 攻击（2022 年 6 月）**：盗取约 1 亿美元，**98% 的被盗资产经由 Tornado Cash 混币**，之后在 Ethereum、BNB Chain、BitTorrent Chain 之间反复跳转，直至 2023 年部分资金再次出现在 Avalanche 和 TRON 链上。

这类攻击展示了当代洗钱的典型模式：**混币 + 跨链 + 多跳中转**，其目的正是通过增加追踪难度来消耗执法和合规资源。

### 1.3 现有工具的局限性

国际刑警组织与相关执法机构的调查显示，**74% 的机构报告称现有区块链调查工具在跨链活动追踪方面存在明显局限**。主流工具（如 Chainalysis Reactor、TRM Labs）虽已具备一定的跨链能力，但其核心算法并未被学术界公开验证，且主要面向商业客户。

从学术研究现状来看，现有文献的主要局限集中在以下几点：

1. **单链为主**：绝大多数 AML 研究以 Bitcoin 或 Ethereum 为单一研究对象，缺乏跨链场景下的分析框架。
2. **黑名单覆盖不足**：现有研究多依赖 OFAC 制裁名单，忽视了稳定币发行方（如 Tether）自行维护的实际冻结名单——后者更贴近真实洗钱被发现的第一现场。
3. **可追溯性未分类讨论**：现有研究鲜少区分"透明桥"与"不透明桥"，而这一分类对于判断是否能继续追踪资金流向至关重要。
4. **图分析缺乏深度控制机制**：现有图分析方法通常设定固定深度，未考虑不同分支的可疑程度差异，导致要么追踪太浅（可规避）、要么开销太大（误伤正常用户）。

---

## 二、研究动机

### 2.1 为什么要做这个工作

本研究的核心动机来自一个现实矛盾：**区块链上的每一笔交易都是公开可查的，但资金流向依然可以被有效隐藏。**

区块链的透明性（transparency）是其与传统银行系统最大的不同——所有交易记录永久保存在公开账本上，任何人都可以查阅。然而，犯罪分子通过三类工具抵消了这种透明性：

1. **混币器（Mixer）**：将多个用户的资金混合后输出，切断输入与输出之间的对应关系。Tornado Cash 在被 OFAC 制裁前累计匿名化了超过 **70 亿美元**的资金流。
2. **不透明跨链桥**：通过流动性池（如 Synapse、Multichain）或做市商模式（如 Orbiter Finance）完成资产转移，但在链上数据中无法找到"这笔钱到底转给了谁"的记录。
3. **干净地址中转**（Money Mule）：通过一连串外观"干净"的中间地址来拉开源地址与目标地址的图谱距离，稀释关联性。

因此，单纯依靠"这个地址是否在黑名单上"的一跳式检查是不够的。现实中的洗钱路径往往需要追踪多跳，才能发现隐藏在中间层的高风险关联。

### 2.2 稳定币黑名单的价值与不足

Tether（USDT 发行方）是目前加密世界中最具执行力的"第一响应人"之一。其维护的黑名单（USDT Blacklist）截止 2025 年 3 月已冻结超过 **8,500 个地址**、涉及资产超过 **42 亿美元**，其中包括与制裁实体、诈骗网络和恐怖主义融资相关的地址。

BlockSec 在 *Following the Frozen: An On-Chain Analysis of USDT Blacklisting* 中分析了 USDT 黑名单的链上行为，发现 **54% 的被冻结地址在冻结发生时，资产已被提前转出**，说明冻结行动常常滞后于实际的资金转移。这也意味着：**真正有价值的是冻结事件发生之前的资金流向追踪，而不仅仅是冻结之后的快照分析。**

本研究正是从这一观察出发：以 USDT 黑名单为"锚点"，向上追踪与黑名单地址有过资金往来的上游地址，并通过跨链追踪延伸到其他链，构建一个多跳、多链的风险评估体系。

### 2.3 普通用户的合规困境：被动污染问题

现有的 AML 工具（Chainalysis、TRM Labs、Elliptic）均以机构用户为主要服务对象，其产品定位是帮助**交易所和监管机构**识别可疑账户。然而，链上的**普通用户**面临的合规风险往往是被动的，且完全缺乏应对工具。

**典型场景如下：**

```
场景一：收款污染
黑名单地址 A ──转账──→ 普通用户 B ──转账──→ 中心化交易所

结果：交易所的 AML 系统检测到 B 的入金来自高风险地址 A，
     B 的账户被冻结或标记为高风险，尽管 B 对此毫不知情。
```

```
场景二：跨链污染扩散
黑名单地址 A → 混币器 → 跨链桥 → 中转地址 C → 普通用户 B

结果：B 在接收来自 C 的转账时，并不知道资金链条的上游存在黑名单地址。
     交易所的 2-hop 或 3-hop 扫描可能同样触发风险警报。
```

这一现象在业界被称为 **"被动污染"（Passive Taint）** 或 **"无辜第三方误伤"**。其核心矛盾在于：

- 区块链是公开透明的，任何人理论上都能查验对方地址的历史——但**分析能力被商业公司垄断**，个人用户无法在发起交易前进行等价的风险自查。
- 交易所的合规政策**不透明且各不相同**：部分交易所追溯 2 跳，部分追溯 5 跳，用户完全不知道自己的入金会被追溯多深。
- 洗钱方有意识地将资金**分散至大量普通地址**（即前文所述的 Money Mule），令这些地址在无意中成为洗钱链条的一环，再由其转入交易所，以此绕过直接黑名单检测。

BlockSec 的分析发现，**54% 的黑名单地址在被冻结前已完成资产转移**——这意味着大量已转出的"污染资金"已经在正常用户地址之间流通，而这些用户本人对此毫不知情。

本研究的目标正是填补这一工具空白：为**普通链上用户**提供一个可自行查验的地址风险评估工具，使其能在发起交易或接受转账前，判断对方地址是否与已知违规行为存在资金关联，从而主动规避被动污染风险。

### 2.4 研究问题的明确定义

综合以上背景，本研究回答以下核心问题：

> **给定一个待查区块链地址，如何系统地识别它与已知黑名单地址之间是否存在资金关联，以及这种关联的风险程度和可信度如何——特别是在资金路径跨越多条区块链、经过混币器或多层中转的场景下？**

具体而言，本研究需解决四个子问题：

- **子问题 1（分类问题）**：如何区分"真正无法追踪的隐匿行为"（混币器、不透明桥）与"可以穿透追踪的跨链行为"（透明桥）？
- **子问题 2（深度问题）**：在多跳追踪中，如何在"追踪深度不足（可规避）"和"追踪开销过大（误伤正常用户）"之间找到合理的平衡点？
- **子问题 3（评分问题）**：如何将多跳、多链的追踪结果量化成可解释的风险评分，使得不同地址之间可以横向比较？
- **子问题 4（比例问题）**：当一个地址同时持有合法资金和污染资金时，如何区分"黑钱"与"白钱"的比例，避免对整个地址一刀切地判定为高风险？

---

## 三、相关文献综述

### 3.1 区块链交易图与 AML 检测

将区块链交易建模为图（Graph）是当前 AML 研究的主流范式。在这一方向上，最具影响力的基础工作来自 Weber 等人（2019 年），他们发布了 **Elliptic Dataset**——一个包含 203,769 个节点和 234,355 条有向边的比特币交易图，其中约 4,500 个节点带有"非法"标注，并在 KDD 2019 的异常检测研讨会上首次提出将图卷积网络（GCN）应用于 AML 分类任务 [1]。该数据集至今仍是学术界最广泛使用的 AML 基准（Benchmark）。

在此基础上，近年来的研究持续在模型架构上推进：

- **Bit-CHetG（2024）**：提出针对异构图的子图对比学习算法，专门用于检测有组织的洗钱团伙，而非单个地址，将图分类任务从节点级推进到子图级 [2]。
- **LB-GLAT（2023）**：引入长程双向图注意力网络，同时处理交易图和反向交易图，捕捉洗钱方惯用的"分散打入、集中打出"模式 [3]。
- **Elliptic2（2024）**：Weber 等人发布的第二代数据集，提供社区级标注，支持对整个洗钱子图（而非单笔交易）进行形态分析，论文标题为 *The Shape of Money Laundering: Subgraph Representation Learning on the Blockchain* [4]。
- **Inspection-L（2022）**：首次将自监督 GNN 应用于 AML，在无标注数据场景下也能提取有效的节点嵌入 [5]。

然而，上述研究有一个共同局限：**均基于单链（主要是 Bitcoin 或 Ethereum），没有讨论资金跨链后如何继续追踪。**

### 3.2 地址聚类与实体识别

在追踪具体资金流向之前，一个前置问题是：区块链上的"地址"未必等同于"实体"（人或组织），同一实体往往控制多个地址。地址聚类（Address Clustering）研究正是为了将散落的地址归并到同一实体。

Victor（2020）提出了专门针对 Ethereum 账户模型的地址聚类启发式方法，利用存款地址模式、空投参与和代币授权机制将地址聚合 [6]。Zhang 等人（2022）则在 Bitcoin 的 UTXO 模型下提出了基于多条启发式规则的聚类方法，通过识别找零地址（Change Address）大幅提升聚合精度 [7]。

地址聚类是商业工具（Chainalysis、Elliptic）的核心能力之一，但相关算法细节并未公开，学术界的开源实现也主要针对 Bitcoin，对 Ethereum 的覆盖仍有缺口。本研究不直接实现地址聚类，但在子节点生成阶段采用交互频率作为代理指标，优先追踪高频交互地址，部分补偿了缺乏聚类能力的不足。

### 3.3 跨链交易的追踪与可追溯性

这一方向是本研究最直接的学术背景，也是近年来增长最快的研究领域之一。

#### 3.3.1 透明桥的追踪方法

**Mazorra 等人（2023/2024）** 在论文 *Tracing Cross-chain Transactions between EVM-based Blockchains: An Analysis of Ethereum-Polygon Bridges*（发表于 Ledger 期刊）中，提出了一套针对 EVM 兼容链之间跨链交易的匹配启发式算法 [8]。其核心思想是：**EVM 兼容链之间，用户地址在不同链上保持一致**（例如同一个 `0xABCD...` 地址在 Ethereum 和 Polygon 上是同一密钥控制的），因此可以通过"时间窗口 + 金额 + 代币类型"的组合匹配算法，将源链上的 Lock 事件与目标链上的 Mint/Release 事件关联起来。该研究在覆盖 2020 年 8 月至 2023 年 8 月的超过 200 万笔跨链交易上实现了高达 **99.65%** 的存款匹配率和 **92.78%** 的取款匹配率。

**Sun 等人（2025）** 在论文 *Track and Trace: Automatically Uncovering Cross-chain Transactions in the Multi-blockchain Ecosystems*（arXiv 2504.01822）中，系统分析了 **12 个主流跨链桥**（包括 Stargate、Celer cBridge、Wormhole、Synapse 等），覆盖 2021 年 4 月至 2024 年 3 月的以太坊源链数据，提出了自动化识别跨链交易的通用框架 [9]。该工作的重要发现之一是：不同桥的"透明程度"差异极大——基于消息传递协议（如 LayerZero）的桥可以通过 API 直接获取对端交易哈希，而基于流动性池的桥（如 Synapse）则几乎不可能在链上数据中找到明确的输入-输出对应关系。

**A Survey of Transaction Tracing Techniques for Blockchain Systems**（arXiv 2510.09624）则从更宏观的视角梳理了区块链交易追踪技术的发展脉络，将现有方法分为：链上事件关联、API 辅助追踪、统计推断和机器学习四大类，并指出跨链追踪是当前最欠缺系统性研究的方向 [10]。

#### 3.3.2 透明桥 vs. 不透明桥：可追溯性分类的重要性

本研究认为，区分**透明桥（traceable bridge）**和**不透明桥（opaque bridge）**是进行有效资金追踪的前提，但这一分类在现有学术文献中尚未得到充分讨论。以下对比说明了两者的本质差异：

| 维度 | 透明桥 | 不透明桥 |
|------|--------|----------|
| **工作机制** | 消息传递协议（LayerZero、Wormhole）或 Rollup 官方桥 | 流动性池（Synapse）、做市商模式（Orbiter、Owlto） |
| **链上对应关系** | 存在唯一 transferId 或共同 txHash，可关联两端 | 用户资金先进入共享池，再由做市商在目标链独立转出，无法关联 |
| **类比** | 银行电汇（有汇款参考号） | 现金存入 ATM 后由不同人取出（无法关联） |
| **洗钱风险** | 低（资金流向可被追踪和追溯） | 高（等同于混币器，资金流向不可追踪） |
| **典型代表** | Stargate, Hop Protocol, Arbitrum/Optimism 官方桥 | Multichain（已崩溃）、Orbiter Finance、Synapse |

Multichain（曾是最大跨链桥之一）于 2023 年因内部问题崩溃，导致约 **1.27 亿美元**资产丢失——这一事件本身也暴露了不透明桥在透明度和可审计性方面的根本性缺陷。

#### 3.3.3 犯罪案例中的跨链洗钱路径

Lazarus Group 在 Ronin Bridge 和 Harmony Bridge 攻击中的洗钱路径（详见第 1.2 节）是迄今为止最被研究的跨链洗钱案例。Chainalysis 的链上追踪显示，在多层桥接和混币操作之后，大部分资金最终流向了 OTC 场外交易商或高风险交易所；执法机构最终追回了约 **3,000 万美元**——仅占 Ronin 被盗总额的约 4.8%。

这一数字揭示了当前追踪能力的上限：即便是资源最充足的商业工具，在面对混币器 + 多链跳转的组合时，追回率也极低。这正是提升自动化追踪工具学术研究价值的根本原因。

### 3.4 多跳风险评分与树状追踪：与本研究最直接相关的先行工作

本节梳理与本研究技术方案最直接相关的三项工作，并在节末给出详细对比表。

#### 3.4.1 奠基工作：Bitcoin 交易风险评分（2014）

**Möser, Böhme & Breuker（2014）** 在 *Towards Risk Scoring of Bitcoin Transactions*（Financial Cryptography 2014）中首次将"从已知违规地址出发、沿交易图传播风险"形式化为一个研究问题 [16]。该工作提出了两种传播策略：

- **Poison（全污染）**：只要资金来源中含有任何违规输入，输出视为完全污染
- **Haircut（按比例）**：污染比例等于违规来源资金占总输入的比例，随混合逐步稀释

这是学术界最早讨论"多跳风险"的工作，被后续几乎所有 Taint Analysis 研究引用。其局限在于发表于 2014 年，研究场景仅限于 Bitcoin 单链，未涉及跨链桥或混币器的特殊处理逻辑。

#### 3.4.2 TaintRank：PageRank 风格的污染传播（2019）

**Hercog & Povšea（2019）** 在 *Taint analysis of the Bitcoin network*（arXiv:1907.01538）中提出 **TaintRank** 算法 [17]，将污染传播类比为 PageRank：

- 构造以地址为节点、交易为有向边的有权图
- 每个节点的污染值由其所有上游节点的加权污染值累加而来
- 污染随传播距离增大自然衰减，最终分布呈幂律形态

TaintRank 以**批量、全局**的方式对整个 Bitcoin 网络进行评分，可为每个地址产生 0-1 的污染指数。与本研究不同的是，它是离线批处理算法，不支持以单个地址为根节点的实时树状查询，亦不支持跨链场景。

#### 3.4.3 Transaction Proximity：Circle 对 Ethereum 全图的 BFS 实践（2025）

**Liao, Zeng, Belenkiy & Hirshman（2025）** 来自 USDC 发行方 Circle，在 *Transaction Proximity: A Graph-Based Approach to Blockchain Fraud Prevention*（arXiv:2505.24284）中，将 BFS 思路应用于整个 Ethereum 历史图 [18]：

- 数据规模：**2.06 亿节点，4.42 亿条边**，覆盖 Ethereum 从创世到 2024 年 5 月的全部交易
- BFS 深度上限：**5 跳**（覆盖 98.2% 的 USDC 活跃持有者）
- 核心指标：**Transaction Proximity**（与受监管交易所的最短跳数）和 **EAI（Easily Attainable Identities）**（直接连接到交易所的地址）
- 关键发现：83% 的已知攻击者地址不是 EAI，21% 距离任何受监管交易所超过 5 跳——说明犯罪地址在图结构上确实倾向于远离"正常流通节点"

值得注意的是，该论文的风险视角与本研究**方向相反但互补**：Transaction Proximity 衡量"距离合法锚点的远近"（越近越合法），本研究衡量"距离违规锚点的远近"（越近越危险）。两种方法理论上可以融合使用，为同一地址从两个方向提供置信度。

#### 3.4.4 与本研究的系统对比

| 特性 | Möser 2014 | TaintRank 2019 | Tx Proximity 2025 | Chainalysis（行业） | **本研究** |
|------|:---:|:---:|:---:|:---:|:---:|
| 跨链追踪 | ❌ | ❌ | ❌ | 部分（未公开） | ✅ |
| 透明桥 vs 不透明桥分类 | ❌ | ❌ | ❌ | ❌ | ✅ |
| 自适应深度（可疑分支加深） | ❌ | ❌ | ❌（固定 5 跳） | ❌ | ✅ |
| 实时单地址查询 | ❌（论文） | ❌（批处理） | ❌（离线分析） | ✅（商业） | ✅ |
| 面向普通用户（非机构） | — | — | — | ❌ | ✅ |
| 黑名单锚点：USDT 冻结名单 | ❌ | ❌ | ❌ | 部分 | ✅ |
| 跳数衰减系数（显式） | ✅ | 隐式 | ❌ | 未公开 | ✅（×0.6） |
| 混币器终止逻辑 | ❌ | ❌ | ❌ | ✅ | ✅ |
| 树状可视化 + Mermaid 导出 | ❌ | ❌ | ❌ | ✅（商业） | ✅ |
| 开源可复现 | — | 部分 | 部分 | ❌ | ✅ |

从对比可以看出：本研究的核心增量在于**跨链追踪框架**（含桥的可追溯性分类）和**自适应深度**机制，这两点在现有学术文献中均无直接先例。Transaction Proximity（2025）是方法论最接近的工作，但它的跨链能力和面向普通用户的定位均未覆盖。

### 3.5 监管框架与现实需求

**FATF（金融行动特别工作组）** 于 2019 年将虚拟资产（VA）和虚拟资产服务提供商（VASP）纳入其反洗钱和反恐融资标准框架（Recommendation 15），并在 2023 年的定向更新报告中指出：在 151 个成员国中，**超过一半尚未实施"旅行规则"（Travel Rule）**，75% 的成员国对 R.15 处于部分合规或不合规状态 [11]。FATF 2023 报告同时特别强调了稳定币被 DPRK 行为者、恐怖主义融资和毒品贩运者使用的显著增长趋势。

上述背景说明：当前合规体系依然存在巨大缺口，自动化、可解释的链上追踪工具具有明确的现实需求，而不仅仅是学术上的研究兴趣。

---

## 四、研究方案概述

基于以上背景和文献，本研究提出一个**以地址为根节点的多链风险溯源图（Multi-Chain Risk Trace Graph）**，核心设计决策如下：

### 4.1 桥的可追溯性分类作为追踪框架的基础

与现有研究不同，本研究将跨链桥的可追溯性（traceability）作为分析框架的一等公民，将其分为：
- **透明桥**：通过协议 API（LayerZero Scan、Hop、Wormhole 等）或事件日志（Rollup 桥）获取对端地址，继续在目标链上展开分析
- **不透明桥**：视同混币器，标记为"追踪断裂"的高风险终止节点

这一分类直接回应了 Sun 等人（2025）在多桥研究中提出的可追溯性差异问题，并在工程实现层面给出了一套可操作的处理方案。

### 4.2 树状追踪与自适应深度

本研究使用 BFS（广度优先搜索）构建资金关联树，并引入**自适应深度（Adaptive Depth）**机制：
- 普通分支使用标准最大深度（默认 3 跳）
- 发现可疑指标（接触黑名单 / 使用混币器 / 使用不透明桥）的分支获得 `depth_bonus` 额外跳数（默认 +1）

这一设计在"追踪不足"和"追踪过度"之间提供了一个数据驱动的平衡点，而不是人为的固定阈值。

### 4.3 风险评分的跳数衰减

参考 AML 实践中"直接关联风险高于间接关联"的共识，本研究引入每跳 **0.6 倍**的风险衰减系数：

| 关联距离 | 衰减后有效风险（原始 100 分） | 风险等级 |
|----------|-------------------------------|----------|
| 直接接触（1 跳） | 60 分 | HIGH |
| 二跳 | 36 分 | MEDIUM |
| 三跳 | 21.6 分 | LOW |
| 四跳及以上 | ≤ 13 分 | 参考 |

### 4.4 中转地址识别

针对"干净地址中转"（Money Mule）这一常见洗钱手段，系统在完成 BFS 展开后对全树进行二次扫描：若一个看似干净的地址的子树中存在黑名单命中，则将其标记为"疑似中转地址（suspect）"，并计算该地址的子树污染评分（contamination score）。

---

## 五、当前进展

### 5.1 已完成工作

本研究目前已完成以下核心模块的实现：

**`aml_analyzer.py` — 单地址分析引擎**
- 接入 Etherscan API 和 TronScan API，完整支持 Ethereum 和 Tron 链
- 实现 USDT 黑名单检测（8,500+ 地址，覆盖 Ethereum 和 Tron）
- 实现跨链桥注册表（`BRIDGE_REGISTRY`），包含 20+ 个桥合约，区分透明/不透明
- 实现混币器识别（Tornado Cash 等 10 个合约）
- 实现 `BridgeTracer`：通过 LayerZero Scan API 获取跨链对端地址
- 实现风险评分（0-100 分）

**`trace_graph.py` — 递归溯源图引擎**
- 基于 BFS 构建多跳资金关联树
- 实现透明桥 → 切链继续追踪
- 实现自适应深度（`depth_bonus`）
- 实现子树风险传播（每跳 0.6 衰减）
- 实现"疑似中转地址"二次标记
- 支持 JSON 导出和 Mermaid 可视化图导出

### 5.2 测试数据选取

系统已具备可测试能力。以下为计划测试的代表性地址：

| 地址 | 类型 | 预期结果 |
|------|------|----------|
| `0x098b716b8aaf21512996dc57eb0615e2383e2f96` | Ronin Bridge 攻击者（Lazarus Group），已在 USDT 黑名单 | 直接黑名单命中，树第一层即终止 |
| `0x7f367cc41522ce07553e823bf3be79a889debe1b` | Lazarus Group 关联地址，已在 USDT 黑名单 | 黑名单命中 |
| 与上述地址有直接交互的上游地址 | 一跳关联（通过 Etherscan 查询） | 风险分 ≈ 60，标记为疑似中转 |
| 使用 Stargate Finance 跨链的测试地址 | 透明桥使用者 | 切链到目标链继续分析 |

### 5.3 后续计划

**近期工程完善（短期）：**
1. 补充 OFAC SDN 名单（覆盖 Harmony 攻击等未被 Tether 冻结的地址）
2. 实现 Hop Protocol、Across Protocol 的对端地址解析
3. 对已知洗钱案例（Ronin/Harmony）进行端到端追踪测试，验证树状结构是否能还原实际洗钱路径
4. 引入时间窗口过滤，避免远古交易引入误报

**中期研究方向：Taint 比例分析**

当前系统对"使用了混币器的地址"或"接收了黑名单转账的地址"采用整体性的风险标记，未能区分该地址中被污染资金与合法资金的比例。这在实践中会导致误伤：一个地址收到了 1 USDT 的黑名单转账，但同时持有 10,000 USDT 的完全合法资金，不应与直接洗钱地址等同对待。

**Taint Analysis（污染比例分析）**是区块链取证领域已有研究的方向，其核心问题是：给定一个地址，其资产中有多大比例可以被溯源到已知违规来源？典型方法包括：
- **FIFO 法**：先入先出，假设地址中最早收到的资金最先被花出
- **按比例法（Haircut）**：污染比例随每次混合按比例稀释
- **Poison 法**：只要有任何污染来源，整个输出均视为污染（最保守）

将 Taint Analysis 引入本系统，可将当前的二元判断（风险/非风险）升级为**比例置信度评分**，更贴近实际合规需求，也更符合 meeting 中提出的"区分黑钱和白钱"目标。

**远期研究方向：合规隐私与白名单混币器**

现有混币器（如 Tornado Cash）因匿名性被监管全面封禁，但其背后存在真实的**合法隐私需求**：用户不希望暴露个人资产状况或商业支付信息。这催生了一个新的研究问题：**能否设计一种混币器，使其既保护用户隐私，又能向外部证明"参与混币的资金来源合法"？**

这一方向在学术上被称为 **Compliant Privacy** 或 **Auditable Privacy**，当前最有前景的技术路径是：
- **零知识证明（Zero-Knowledge Proof, ZKP）**：用户可以在不暴露来源地址和金额的情况下，向验证方证明"我的资金未曾接触过黑名单地址"。Railgun 协议已在此方向上进行了工程探索，并在 Tornado Cash 被制裁后显著增长（2025 年市占率达 71%）。
- **环签名（Ring Signature）**：允许用户匿名参与交易，同时可配合黑名单检查机制实现有限度的可审计性。

该方向是本项目的前瞻性研究内容，超出当前中期阶段的实现范围，但作为研究议题值得在报告中提出，以展示项目在技术和政策层面的完整视野。

---

## 参考文献

[1] Weber, M., Domeniconi, G., Chen, J., Weidele, D. K. I., Bellei, C., Robinson, T., & Leiserson, C. E. (2019). **Anti-Money Laundering in Bitcoin: Experimenting with Graph Convolutional Networks for Financial Forensics.** *KDD Workshop on Anomaly Detection in Finance.* arXiv:1908.02591.

[2] Xu, Z. et al. (2024). **Bitcoin Money Laundering Detection via Subgraph Contrastive Learning.** *Entropy, 26*(3), 211. PMC10969714.

[3] Alarab, I., & Prakoonwit, S. (2023). **LB-GLAT: Long-Term Bi-Graph Layer Attention Convolutional Network for Anti-Money Laundering in Transactional Blockchain.** *Mathematics, 11*(18), 3927.

[4] Bellei, C. et al. (2024). **The Shape of Money Laundering: Subgraph Representation Learning on the Blockchain with the Elliptic2 Dataset.** arXiv:2404.19109.

[5] Lo, W. W. et al. (2022). **Inspection-L: Self-Supervised GNN Node Embeddings for Money Laundering Detection in Bitcoin.** arXiv:2203.10465.

[6] Victor, F. (2020). **Address Clustering Heuristics for Ethereum.** *Financial Cryptography and Data Security (FC 2020).* IFCA.

[7] Zhang, X. et al. (2022). **Bitcoin Address Clustering Method Based on Multiple Heuristic Conditions.** *IET Blockchain, 2*(1).

[8] Mazorra, B. et al. (2023). **Tracing Cross-Chain Transactions Between EVM-Based Blockchains: An Analysis of Ethereum-Polygon Bridges.** *Ledger Journal.* arXiv:2504.15449.

[9] Sun, X. et al. (2025). **Track and Trace: Automatically Uncovering Cross-chain Transactions in the Multi-blockchain Ecosystems.** arXiv:2504.01822.

[10] Ren, J. et al. (2025). **A Survey of Transaction Tracing Techniques for Blockchain Systems.** arXiv:2510.09624.

[11] FATF (2023). **Targeted Update on Implementation of the FATF Standards on Virtual Assets and Virtual Asset Service Providers.** Financial Action Task Force. June 2023.

[12] Chainalysis (2024). **2024 Crypto Money Laundering Report.** Chainalysis Inc.

[13] Elliptic (2023). **$7 Billion in Crypto Laundered Through Cross-Chain Services.** Elliptic Enterprise Ltd.

[14] BlockSec (2023). **Following the Frozen: An On-Chain Analysis of USDT Blacklisting and Its Links to Terrorist Financing.** BlockSec Blog.

[15] Weber, M. & Bellei, C. (2019). **Elliptic Data Set.** Kaggle / Elliptic. https://www.kaggle.com/datasets/ellipticco/elliptic-data-set

[16] Möser, M., Böhme, R., & Breuker, D. (2014). **Towards Risk Scoring of Bitcoin Transactions.** *Financial Cryptography and Data Security Workshops (FC 2014).* Springer. https://maltemoeser.de/paper/risk-scoring.pdf

[17] Hercog, U., & Povšea, A. (2019). **Taint Analysis of the Bitcoin Network.** arXiv:1907.01538.

[18] Liao, G., Zeng, Z., Belenkiy, M., & Hirshman, J. (2025). **Transaction Proximity: A Graph-Based Approach to Blockchain Fraud Prevention.** Circle Research. arXiv:2505.24284.
