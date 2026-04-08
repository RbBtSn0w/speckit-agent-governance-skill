# 治理Agents.md 和 spec-kit中的 memory constitution.md, 确保各自职责边界清晰

## Background Context

This project uses a minimal governance model for AI-agent collaboration.
Only two persistent governance documents are maintained:

AGENTS.md at the repository root
.specify/memory/constitution.md as the optional project constitution
The constitution is the source of truth for durable project principles, hard constraints, architectural boundaries, safety requirements, and quality expectations. AGENTS.md is the source of truth for agent operating behavior, including workflow, communication norms, tool usage, validation steps, and the operationalization of constitutional rules.

To keep the system maintainable, the project intentionally avoids introducing additional long-lived governance markdown files. Instead, all logic related to boundary definition, conflict detection, precedence, synchronization, and runtime memory assembly is centralized in a dedicated governance skill. This skill acts as the professional maintenance layer between the two documents, ensuring that they remain clear in scope, internally consistent, and optimized for effective AI-agent memory usage.


目标: 做成**一个治理型 skill**，只维护这两个文件：`AGENTS.md` 与 `.specify/memory/constitution.md`。不再引入更多长期驻留的 `.md` 文件；把“边界、冲突、优先级、同步策略”都收敛到**命令/脚本/临时报告**里。

## 核心定位

这个 skill 的目标不是“写更多文档”，而是：

- 让 **`constitution.md` 成为原则源**
- 让 **`AGENTS.md` 成为执行源**
- 自动检测两者：
  - 是否重复
  - 是否冲突
  - 是否缺失映射
  - 是否可被 agent 正确装配到 memory
- 在更新任一文件时，给出**最小必要修复**

一句话：

> 用一个专门的 governance skill，维护两个核心文件的职责边界、同步一致性和运行时装配质量。

---

# 一、最简架构

只保留：

- `AGENTS.md`
- `.specify/memory/constitution.md`（可选，没有也能工作）

再增加的不是长期文档，而是**能力组件**：

1. 一个 command  
   - `references/governance.md`

2. 几个脚本  
   - 用于检查、分类、比较、生成建议

3. 一个轻量配置文件（可选）
   - 不是必须，但建议有一个机器可读配置
   - 比如 `assets/governance.yml`

如果你连配置文件都想省，可以把默认规则直接写进 skill。

---

# 二、职责边界，先固定死

这是整个 skill 的基础。

## `constitution.md` 的职责
只允许放：

- 项目原则
- 架构硬约束
- 安全/合规要求
- 质量底线
- 兼容性规则
- 治理和变更原则

特点：
- 稳定
- 高层
- 不面向某个 agent
- 不写具体执行步骤

---

## `AGENTS.md` 的职责
只允许放：

- agent 工作流
- 分析/实现/验证顺序
- 工具使用习惯
- 何时提问、何时停止
- 输出格式
- 如何把 constitution 落实为动作

特点：
- 可执行
- 面向 agent
- 可随着工具链变化更新
- 不能重新定义项目原则

---

## 固定优先级
skill 内置唯一裁决规则：

1. `.specify/memory/constitution.md`
2. `AGENTS.md`
3. 当前任务输入

也就是：
- constitution 决定“什么不能违背”
- AGENTS 决定“如何执行”
- task 只能在不冲突时补充细节

---

# 三、设计一个单一核心 skill

建议名字：`speckit-agent-governance`

它统一处理以下场景：

1. 更新 constitution
2. 更新 AGENTS
3. 检查两者冲突
4. 从一方变化推导另一方是否要同步
5. 生成给 agent 运行时使用的“压缩上下文”

---

# 四、这个 skill 应该具备的能力

## 1. Analyze
读取两份文件，拆成规则单元。

每条规则都要被分类为：

- `principle`
- `constraint`
- `workflow`
- `communication`
- `tooling`
- `validation`
- `governance`

然后判断它更该属于：
- constitution
- AGENTS

---

## 2. Detect
识别 4 类问题

### A. 重复
同一规则在两个文件中都写了，而且表述接近。

### B. 冲突
比如：

- constitution：API 变更必须向后兼容
- AGENTS：重构时可直接修改 API，只需在 PR 说明

这是明显冲突。

### C. 越权
AGENTS 定义了本应由 constitution 才能定义的原则。

### D. 缺口
constitution 有原则，但 AGENTS 没有把它转译成执行动作。

例如：
- constitution 要求测试
- AGENTS 没写“改动后运行相关测试”

---

## 3. Reconcile
给出修复建议：

- 保留在 constitution
- 下放到 AGENTS
- 从 AGENTS 删除
- 在 AGENTS 中增加执行性重述
- 标记待人工确认

---

## 4. Update
根据用户选择，更新：
- 只改 constitution
- 只改 AGENTS
- 两者联动修复

---

## 5. Assemble
为 agent 运行时生成一个“最优 memory 视图”。

注意：**不是新增常驻 markdown 文件**，而是运行时生成一个临时产物或输出摘要。

比如输出：

- constitutional constraints summary
- agent workflow summary
- active precedence notes
- risk flags

这一步非常关键，因为你最终是为了“AI agent 的 memory 使用最佳状态”。

---

# 五、推荐的 command 设计

你可以定义一个：

```markdown
references/governance.md
```

它不取代 spec-kit 下的 `commands/constitution.md` command，而是成为上层 skill。

---

## 它的职责描述可以写成

> Analyze and reconcile the relationship between `AGENTS.md` and `.specify/memory/constitution.md`, preserving clear ownership, preventing conflicts, and optimizing agent runtime memory usage.

---

## 它的执行流程建议

### 1. 输入
支持以下几种输入：

- “更新 constitution”
- “更新 AGENTS”
- “对齐两者”
- “检查冲突”
- “生成 runtime memory summary”

---

### 2. 读取文件
- `AGENTS.md`
- `.specify/memory/constitution.md`（若存在）

如果 constitution 不存在：
- 系统退化为只治理 `AGENTS.md`
- 并提示当前项目采用单源治理

---

### 3. 规则抽取
把文档拆成 rule units：

- id
- source_file
- heading
- text
- type
- norm_strength (`MUST`, `SHOULD`, `MAY`)
- topic
- actionability
- owner_candidate

---

### 4. 归属判断
应用内置判断器：

#### 放 constitution 的信号
- 包含长期约束
- 面向项目整体
- 涉及安全/架构/合规/兼容
- 与具体 agent 无关

#### 放 AGENTS 的信号
- 包含操作步骤
- 面向 agent 行为
- 涉及提问/执行/验证/工具
- 属于 workflow

---

### 5. 冲突分析
输出：
- 重复项
- 冲突项
- 越权项
- 缺口项

---

### 6. 生成修复计划
例如：

- Move rule X from AGENTS.md to constitution.md
- Remove duplicate rule Y from constitution.md
- Add operational check in AGENTS.md for constitutional rule Z

---

### 7. 更新目标文件
若用户允许，则回写文件。

---

### 8. 输出最终摘要
包括：
- 当前治理模式：单源 / 双源
- 发现的问题数
- 已修复项
- 待确认项
- 建议 commit message

---

# 六、最关键：怎么“专业地”判断边界

这部分最好不要只靠 prompt，要靠**规则 + 脚本**共同完成。

---

## 规则分类模型

建议给每条规则打标签。

### Constitution 标签
- `security`
- `compliance`
- `architecture`
- `compatibility`
- `quality-bar`
- `governance`

### AGENTS 标签
- `workflow`
- `communication`
- `tool-usage`
- `planning`
- `editing`
- `validation`
- `handoff`

然后规定：

- `security/compliance/architecture/compatibility/governance`  
  默认归 constitution
- `workflow/tool-usage/communication/planning/editing`  
  默认归 AGENTS
- `validation/quality-bar`  
  可双边出现，但：
  - constitution 写“要求”
  - AGENTS 写“如何执行检查”

这就是“专业服务”的核心。

---

# 七、你需要哪些脚本或资源

这是最实际的部分。

## 必需脚本 1：规则抽取器
例如：

- `scripts/governance_extract_rules.py`

功能：
- 读取 markdown
- 按标题/列表/段落切分规则
- 识别规范词：`MUST/SHOULD/MAY`
- 输出结构化 JSON

输出示例：

```json
[
  {
    "id": "agents-12",
    "source": "AGENTS.md",
    "heading": "Validation",
    "text": "Run relevant tests before finalizing changes.",
    "norm_strength": "MUST",
    "topic": "validation",
    "candidate_owner": "agents"
  }
]
```

---

## 必需脚本 2：规则分类器
例如：

- `scripts/governance_classify_rules.py`

功能：
- 基于关键词、标题、模式判断规则属于：
  - constitution
  - agents
- 给出置信度和原因

---

## 必需脚本 3：冲突检测器
例如：

- `scripts/governance_detect_conflicts.py`

功能：
- 比较两个规则集
- 识别：
  - duplicate
  - overlap
  - contradiction
  - shadowing
  - missing operationalization

---

## 必需脚本 4：同步建议生成器
例如：

- `scripts/governance_suggest_sync.py`

功能：
- 根据分析结果生成修复建议
- 可输出 markdown report 或 JSON plan

---

## 可选脚本 5：runtime memory assembler
例如：

- `scripts/governance_build_context.py`

功能：
- 从 constitution + AGENTS 生成一个运行时摘要
- 压缩成 agent 可消费的短上下文

输出例如：

```json
{
  "constraints": [
    "Preserve backward compatibility.",
    "Never expose secrets."
  ],
  "workflow": [
    "Inspect before editing.",
    "Prefer minimal diffs.",
    "Run relevant tests."
  ],
  "precedence": [
    "constitution overrides AGENTS"
  ]
}
```

这个非常适合作为 runtime 注入材料。

---

# 八、建议的最小资源文件

如果你愿意增加一个很轻量的机器配置文件，我建议只加这个：

## `assets/governance.yml`
不是文档，而是规则配置。

例如：

```yaml
precedence:
  - constitution
  - agents
  - task

ownership:
  constitution:
    - security
    - compliance
    - architecture
    - compatibility
    - governance
  agents:
    - workflow
    - communication
    - tool_usage
    - planning
    - editing

operationalization:
  allowed_from_constitution_to_agents: true
  allow_agents_to_redefine_constitution: false

runtime:
  summarize_constitution: true
  include_agents_full_by_default: true
```

这个文件非常值，因为：
- 机器可读
- 不增加维护心智负担
- 让脚本稳定
- 比再加多个 markdown 文档更轻

---

# 九、建议的 command 模板结构

下面是你这个核心 skill 该包含的模块。

## `references/governance.md` 应有：

### 1. User Input
接收：
- 更新请求
- 检查请求
- 对齐请求

### 2. Pre-Execution Checks
- 检查 `AGENTS.md`
- 检查 `.specify/memory/constitution.md`
- 检查可选 `.specify/governance.yml`

### 3. Analysis
- 提取规则
- 分类
- 比较
- 确定权属

### 4. Reconciliation
- 基于 precedence 生成方案

### 5. Validation
- 无越权规则
- 无未解释冲突
- 无高风险重复定义

### 6. Output
- 更新文件
- 给出 sync report
- 给出 runtime context summary

---

# 十、实现方式建议

## 方案 A：纯 prompt 驱动
优点：
- 快
- 易做

缺点：
- 不稳定
- 大文件时容易漂
- 冲突判断容易不一致

**不建议单独使用。**

---

## 方案 B：prompt + 脚本辅助
这是最推荐的。

- prompt 负责流程编排、解释、回写
- 脚本负责：
  - 提取
  - 分类
  - 比较
  - 生成结构化报告

优点：
- 稳定
- 可重复
- 可测试
- 更像专业 skill

---

## 方案 C：全 AST/规则引擎
最强，但太重。

除非你做平台化产品，否则没必要。

---

# 十一、最佳落地方案

如果你要一个维护成本最低、效果最好的版本，我建议：

## 针对文件
- `AGENTS.md`
- `.specify/memory/constitution.md`（可选）

## 新增一个 command
- `references/governance.md`

## 新增一个轻配置
- `assets/governance.yml`（可选但推荐）

## 新增 4 个脚本
- `extract_rules.py`
- `classify_rules.py`
- `detect_conflicts.py`
- `build_context.py`

这已经足够形成一个成熟的专业 skill 了。

---
