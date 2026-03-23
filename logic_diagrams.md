# 系统逻辑图集

---

## 图 1：系统整体流程

```mermaid
flowchart TD
    INPUT([🔍 输入：待查地址]) --> INIT

    INIT["初始化\n加载 USDT 黑名单 ~8500 个地址\n创建根节点 depth=0"]
    INIT --> BFS_START

    BFS_START["BFS 队列初始化\nqueue = [root_node]"]
    BFS_START --> LOOP

    LOOP{队列非空？\n且节点数 < max_nodes？}
    LOOP -- 否 --> POSTPROCESS
    LOOP -- 是 --> DEQUEUE

    DEQUEUE["取出队列首节点\nnode = queue.popleft()"]
    DEQUEUE --> VISITED{已访问过？}
    VISITED -- 是 --> LOOP
    VISITED -- 否 --> ANALYZE

    ANALYZE["单地址分析 AMLAnalyzer.analyze()"]
    ANALYZE --> API["查询链上数据\nEtherscan / TronScan API"]
    API --> TIMEFILTER["时间窗口过滤\n丢弃 N 天前的交易"]
    TIMEFILTER --> CHECKS

    CHECKS["并行检测"]
    CHECKS --> C1["黑名单匹配\nUSIC blacklist.csv"]
    CHECKS --> C2["桥合约识别\n20+ 个注册合约"]
    CHECKS --> C3["混币器识别\nTornado Cash 等"]
    C1 & C2 & C3 --> SCORE["风险评分计算\n0–100 分"]

    SCORE --> CLASSIFY["节点分类"]

    CLASSIFY --> TYPE{分类结果}

    TYPE -- "在黑名单" --> T_BL["🔴 blacklisted\n权重=100\n⛔ 终止节点"]
    TYPE -- "用过混币器\n或不透明桥" --> T_SUS["⚠️ suspect\n权重=35\n⛔ 终止节点\n资金流向断裂"]
    TYPE -- "1跳黑名单≥3\n或评分≥60" --> T_HR["🟡 high_risk\n权重=50\n✅ 继续展开"]
    TYPE -- "经透明桥到达" --> T_BD["🔵 bridge_dst\n权重=20\n✅ 切换目标链"]
    TYPE -- "无特殊标记" --> T_CL["⚪ clean\n权重=0\n✅ 继续展开"]

    T_BL --> LOOP
    T_SUS --> LOOP

    T_HR & T_BD & T_CL --> DEPTH{depth < local_max_depth？}
    DEPTH -- 否 --> LOOP
    DEPTH -- 是 --> CHILDREN

    CHILDREN["生成子节点 _get_children()\n最多 max_children 个"]
    CHILDREN --> P1["① 透明桥对端地址\n最高优先级"]
    CHILDREN --> P2["② 1跳黑名单地址\n直接标记不再分析"]
    CHILDREN --> P3["③ 混币器/不透明桥合约\n终止节点展示"]
    CHILDREN --> P4["④ 普通高频对手方\n按交互次数降序"]

    P1 & P2 & P3 & P4 --> ADAPTDEPTH["自适应深度\n可疑节点 local_max_depth + depth_bonus"]
    ADAPTDEPTH --> ENQUEUE["加入 BFS 队列"]
    ENQUEUE --> LOOP

    POSTPROCESS["BFS 完成后处理"]
    POSTPROCESS --> PROPAGATE["_propagate_risk()\n后序遍历：风险向上传播\n每跳 × 0.6 衰减"]
    PROPAGATE --> RECLASSIFY["_reclassify_suspects()\n标记疑似中转地址\nclean 节点若子树含黑名单 → suspect"]
    RECLASSIFY --> OUTPUT

    OUTPUT["输出结果"]
    OUTPUT --> O1["🖥 终端树状图\n含颜色和风险评级"]
    OUTPUT --> O2["📄 JSON 导出\n完整节点结构"]
    OUTPUT --> O3["📊 Mermaid 图导出\n.md 文件，可渲染"]
```

---

## 图 2：节点分类决策树

```mermaid
flowchart TD
    START(["分析一个地址"]) --> Q1

    Q1{"在 USDT 黑名单中？"}
    Q1 -- 是 --> BL["🔴 blacklisted\n直接被 Tether 冻结\n风险权重 = 100\n⛔ 终止，不再展开"]

    Q1 -- 否 --> Q2{"使用过混币器？\n或使用过不透明桥？"}
    Q2 -- 是 --> SUS["⚠️ suspect\n资金流向在此中断\n无法继续追踪\n风险权重 = 35\n⛔ 终止，不再展开"]

    Q2 -- 否 --> Q3{"1跳黑名单地址 ≥ 3 个\n或风险评分 ≥ 60？"}
    Q3 -- 是 --> HR["🟡 high_risk\n综合评分高\n风险权重 = 50\n✅ 继续展开子节点"]

    Q3 -- 否 --> Q4{"是否经由透明桥到达此节点？\n即 via_bridge != null"}
    Q4 -- 是 --> BD["🔵 bridge_dst\n透明桥对端地址\n已切换到目标链\n风险权重 = 20\n✅ 在目标链继续展开"]

    Q4 -- 否 --> CL["⚪ clean\n目前无已知风险\n风险权重 = 0\n✅ 继续展开子节点\n——但子树分析后可能升级为 suspect"]

    NOTE1["📌 注意：混币器合约本身\n（如 Tornado Cash 地址）\n在 _get_children 中被显式设为 mixer 节点\n与"使用了混币器的用户地址"是两个不同节点"]
    SUS -.-> NOTE1
```

---

## 图 3：五种洗钱路径及系统应对策略

```mermaid
flowchart LR
    subgraph S1["模式①：直接接触"]
        direction TB
        A1["用户地址"] -->|"直接转账"| B1["🔴 黑名单地址"]
        B1 --> R1["系统响应：\n1跳命中，风险分 +60\n标记 high_risk 或 blacklisted"]
    end

    subgraph S2["模式②：混币器隐匿"]
        direction TB
        A2["用户地址"] -->|"存入"| M2["🔴 Tornado Cash\n(混币器合约)"]
        M2 -.->|"资金流向未知\n无法追踪"| X2["??? 未知接收方"]
        M2 --> R2["系统响应：\n标记为 suspect\n追踪终止"]
    end

    subgraph S3["模式③：透明跨链桥"]
        direction TB
        A3["ETH 用户地址"] -->|"存入"| BR3["Stargate Bridge\n(透明桥)"]
        BR3 -->|"LayerZero API\n解析对端地址"| C3["ARB 对端地址"]
        C3 --> R3["系统响应：\n切链继续分析\n创建 bridge_dst 节点"]
    end

    subgraph S4["模式④：不透明跨链桥"]
        direction TB
        A4["用户地址"] -->|"存入流动性池"| BR4["Synapse / Multichain\n(不透明桥)"]
        BR4 -.->|"池内混合\n无法对应"| X4["??? 目标链接收方"]
        BR4 --> R4["系统响应：\n等同混币器\n标记 suspect，追踪终止"]
    end

    subgraph S5["模式⑤：多跳中转（Money Mule）"]
        direction TB
        BL5["🔴 黑名单地址"] -->|"转账"| C5["中转地址 A\n(看似干净)"]
        C5 -->|"转账"| D5["中转地址 B\n(看似干净)"]
        D5 -->|"转账"| E5["普通用户"]
        E5 --> R5["系统响应：\n树状展开发现子树有黑名单\n中转地址回溯标记为 suspect\n污染评分 × 0.6^深度 传播"]
    end
```

---

## 图 4：风险评分与跳数衰减

```mermaid
flowchart TD
    subgraph DECAY["风险衰减传播示意（黑名单地址风险原始值 = 100）"]
        direction TB

        ROOT["根节点（待查地址）\n最终接收到的传播风险"]

        D1["深度 1 节点\n衰减系数 = 1.0\n传播风险 = 60\n▶ 高风险 HIGH"]

        D2["深度 2 节点\n衰减系数 = 0.6\n传播风险 = 36\n▶ 中风险 MEDIUM"]

        D3["深度 3 节点\n衰减系数 = 0.36\n传播风险 = 21.6\n▶ 中低风险"]

        D4["深度 4 节点\n衰减系数 = 0.216\n传播风险 = 13\n▶ 低风险 LOW"]

        BL["🔴 黑名单地址\n自身风险 = 100"]

        BL -->|"× 0.6"| D4
        D4 -->|"× 0.6"| D3
        D3 -->|"× 0.6"| D2
        D2 -->|"× 0.6"| D1
        D1 -->|"× 0.6"| ROOT
    end

    subgraph ADAPTIVE["自适应深度示意"]
        direction TB
        N0["根节点\nmax_depth = 3"] --> N1A["普通子节点 A\nlocal_max = 3"]
        N0 --> N1B["可疑子节点 B\n发现混币器交互\nlocal_max = 3+1 = 4"]

        N1A --> N2A["深度2 → 正常展开"]
        N2A --> N3A["深度3 → 到达上限，停止"]

        N1B --> N2B["深度2 → 正常展开"]
        N2B --> N3B["深度3 → 仍在上限内，继续"]
        N3B --> N4B["深度4 → 到达可疑分支上限，停止"]
    end
```

---

## 图 5：数据流与 API 依赖

```mermaid
flowchart LR
    subgraph INPUT_LAYER["输入层"]
        ADDR["目标地址\n0x... 或 Tron"]
        BL_CSV["usdt_blacklist.csv\n~8,500 条"]
    end

    subgraph DATA_LAYER["数据获取层"]
        ETH_API["Etherscan API\ntxlist / tokentx / getLogs\nbalance"]
        TRON_API["TronScan API\ntransactions"]
        LZ_API["LayerZero Scan API\napi.layerzeroscan.com\n跨链对端解析"]
        BLOCKSCOUT["Blockscout\nEtherscan 不可用时 fallback"]
    end

    subgraph ANALYSIS_LAYER["分析层"]
        AML["AMLAnalyzer\n单地址分析引擎"]
        TRACER["BridgeTracer\n透明桥对端地址解析"]
        GRAPH["TraceGraph\nBFS 树状追踪引擎"]
    end

    subgraph OUTPUT_LAYER["输出层"]
        TREE["终端彩色树状图"]
        JSON_OUT["JSON 结构文件"]
        MERMAID_OUT["Mermaid 图 .md"]
    end

    ADDR --> AML
    BL_CSV --> AML
    AML <--> ETH_API
    AML <--> TRON_API
    AML <--> BLOCKSCOUT
    TRACER <--> LZ_API
    AML --> TRACER
    AML --> GRAPH
    GRAPH --> TREE
    GRAPH --> JSON_OUT
    GRAPH --> MERMAID_OUT
```
