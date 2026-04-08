# Agent Governance Alignment

## Product Definition v2

### 1. Product Positioning

`Agent Governance Alignment` is a governance alignment service for AI agents.

Its role is not to generate more governance documentation, but to help projects continuously maintain alignment across:

- durable principles
- executable agent rules
- runtime agent context

### 2. Core Problem

It addresses long-term governance drift, not writing style:

- project principles and agent execution guides drift apart
- the same rule appears in multiple governance layers
- agent workflows conflict with higher-level constraints
- governance documents become too long for efficient agent runtime use
- after repeated edits, it becomes hard to judge whether governance is still aligned

### 3. Product Goals

The product has three core goals:

- `Alignment`: keep principle and execution boundaries clear
- `Detection`: find duplicates, conflicts, overreach, and gaps quickly
- `Compression`: produce compact, high-signal runtime governance summaries for agents

### 4. Non-Goals

This product should not be defined as:

- an automatic fixer for all governance issues
- a semantic authority that makes final policy decisions
- a general-purpose documentation management system
- a mandatory baseline component for every project
- a replacement for human governance judgment

It is a governance support service, not the ultimate governance authority.

### 5. Target Users

Best-fit users:

- projects that maintain both `AGENTS.md` and a constitution-like document
- teams with multi-agent or multi-person collaboration
- projects where governance docs evolve over time
- workflows that need compact runtime governance context
- teams that want governance checks in workflow or CI

Poor-fit users:

- single-maintainer, low-change projects
- projects with only one lightweight agent rules file
- projects that do not intend to maintain a governance structure over time

### 6. Core Capabilities

#### A. Governance Drift Detection

Given governance inputs, detect:

- `duplicate`
- `conflict`
- `overreach`
- `gap`

#### B. Ownership Classification

Classify rules into governance roles such as:

- principle / constraint
- workflow / communication / validation
- constitution-owned / agent-owned

#### C. Repair Guidance

Provide minimal repair guidance instead of only reporting errors.

#### D. Runtime Governance Context

Generate agent-consumable summaries such as:

- active constraints
- executable workflow
- precedence notes
- residual risks

#### E. Trust Signals

Help users judge whether results are trustworthy:

- confidence
- ignored findings
- residual findings
- strict vs pragmatic mode
- merge readiness

### 7. Product Forms

This product should not be tied to a single delivery format. It should support multiple access layers:

#### 1. Skill

For interactive agent-session checks, summaries, and guidance.

#### 2. Extension

For structured project environments such as spec-kit style repositories.

#### 3. Service / CLI / CI

For long-term team usage, automation, and governance gates.

The key point:

- the `skill` is not the product itself
- a `spec-kit extension` is not the product itself
- both are integration surfaces for the same governance service

### 8. MVP Boundary

The first stage should retain only the most durable capabilities:

- extract
- classify
- detect
- build_context

The second stage can add:

- rewrite hints
- ignore / waiver support
- confidence / score
- human-readable summary

Later stages can consider:

- patch preview
- CI gating
- multi-repo governance dashboards

### 9. Maturity Statement

The correct maturity positioning is:

`Governance advisory service`

Not:

`Authoritative governance engine`

That means:

- it can assist governance decisions
- it can accelerate governance review
- it can compress runtime context
- it should not claim to guarantee governance correctness automatically

### 10. Evolution Roadmap

#### Phase 1

Stabilize trustworthiness:

- single-source consistency
- stronger topic classification robustness
- runtime summary boundary correctness
- truthful config surface

#### Phase 2

Improve usability:

- rewrite hints
- layered repair plans
- readable summaries
- false-positive suppression

#### Phase 3

Evolve into infrastructure:

- CI integration
- MCP / API surface
- trend analysis
- governance quality scoring

### 11. One-Sentence Definition

English:

> A governance alignment service for AI agents that detects drift between durable project principles and executable agent behavior, provides actionable findings, and assembles compact runtime governance context.

Chinese:

> 一个面向 AI agent 的治理对齐服务，用于检测项目原则与 agent 执行规则之间的漂移，提供可执行建议，并生成精简的运行时治理上下文。
