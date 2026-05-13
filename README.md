<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+" />
  <img src="https://img.shields.io/badge/Version-v1.0.0-green.svg" alt="Version" />
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License" />
  <img src="https://img.shields.io/badge/Rules-76-orange.svg" alt="76 Rules" />
  <img src="https://img.shields.io/badge/Dependencies-0-success.svg" alt="Zero Dependencies" />
  <img src="https://img.shields.io/badge/Frameworks-React%20%7C%20Vue%20%7C%20Svelte%20%7C%20Angular-9cf.svg" alt="Frameworks" />
</p>

<h1 align="center">🩺 FrameScore</h1>

<p align="center">
  <strong>轻量级前端框架代码健康智能评分引擎</strong><br/>
  <em>A Lightweight Frontend Framework Code Health Intelligent Scoring Engine</em>
</p>

<p align="center">
  <a href="https://github.com/gitstq/FrameScore">GitHub</a> ·
  <a href="#快速开始">快速开始</a> ·
  <a href="#规则列表">规则列表</a> ·
  <a href="#评分体系">评分体系</a>
</p>

---

> **语言切换 / Language Switch**
>
> [简体中文](#) | [繁體中文](#繁體中文) | [English](#english)

---

<a id="简体中文"></a>

# 🇨🇳 简体中文

---

## 🎉 项目介绍

FrameScore 是一款专为前端开发者打造的**轻量级代码健康智能评分引擎**。它能够深入扫描你的前端项目，基于 **76 条内置规则**对代码质量进行全面体检，最终输出一个直观的 **0-100 健康评分**及 **A+ 到 F 等级评定**。

### 💡 为什么需要 FrameScore？

在日常前端开发中，我们常常面临以下痛点：

- **代码审查耗时耗力** — 人工逐行检查代码规范和潜在问题，效率低下
- **缺少统一的质量度量** — 团队对"好代码"缺乏可量化的标准
- **框架最佳实践难以落地** — React、Vue、Svelte、Angular 各有最佳实践，但难以全面覆盖
- **安全漏洞容易被忽视** — XSS、注入攻击等安全隐患在日常开发中屡见不鲜
- **性能问题难以定位** — 不必要的重渲染、内存泄漏等问题隐藏在代码深处

### 🌟 核心差异化优势

- **零外部依赖** — 纯 Python 标准库实现，安装即用，无需配置复杂环境
- **多框架支持** — 一站式覆盖 React、Vue、Svelte、Angular 四大主流框架
- **智能评分体系** — 科学加权算法，将复杂的代码分析结果转化为直观的 0-100 分数
- **并行分析引擎** — 多线程并行扫描，大型项目也能快速完成分析
- **Git 历史追踪** — 自动记录每次评分，追踪代码质量变化趋势
- **灵活输出格式** — 支持 JSON、表格、Markdown 三种输出格式，方便集成到 CI/CD

### 🎯 灵感来源

FrameScore 的灵感来源于代码质量评分工具（如 Code Climate、SonarQube）的理念，但专注于前端框架特有的代码模式和最佳实践。我们希望为前端团队提供一个**开箱即用、零配置、轻量高效**的代码健康评估方案。

---

## ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🏥 **智能健康评分** | 基于 76 条规则的综合评分，0-100 分直观反映代码健康状态 |
| 📊 **A+ 到 F 等级** | 科学的等级划分，快速了解项目质量水平 |
| ⚡ **并行分析引擎** | 多线程并行扫描，大幅提升大型项目分析速度 |
| 🔍 **76 条内置规则** | 覆盖 React、Vue、Svelte、Angular 及通用、安全、性能六大类别 |
| 📦 **依赖分析** | 自动检测项目依赖，识别缺失锁文件和非语义化版本 |
| 🔗 **Git 集成** | 自动追踪评分历史，可视化代码质量变化趋势 |
| 📋 **多种输出格式** | 支持 JSON、表格、Markdown 三种格式，满足不同使用场景 |
| 🎯 **框架自动检测** | 智能识别项目使用的框架，自动加载对应规则集 |
| 🚫 **零外部依赖** | 纯 Python 标准库实现，安装即用无负担 |
| ⚙️ **灵活配置** | 支持按严重程度过滤、指定框架、自定义工作线程数等 |

---

## 🚀 快速开始

### 📋 环境要求

- **Python** 3.8 或更高版本
- 无需安装任何第三方依赖

### 📦 安装

```bash
# 从 PyPI 安装（推荐）
pip install framescore

# 从 GitHub 安装最新版本
pip install git+https://github.com/gitstq/FrameScore.git
```

### 🏃 快速运行

```bash
# 扫描当前目录
framescore scan .

# 扫描指定项目
framescore scan /path/to/your/project

# 查看版本信息
framescore -v
```

### 📸 输出示例

扫描完成后，你将看到类似以下的输出：

```
  ╔══════════════════════════════════════╗
  ║         FrameScore v1.0.0           ║
  ║   Code Health Scoring Engine        ║
  ╚══════════════════════════════════════╝

  Scanning project...
  Framework:  react
  Files:      42 (3,856 lines)
  Deps:       28 (18 prod, 10 dev)
  Branch:     main
  Commits:    156

  Completed in 2.3s | 23 issues found | Score: 78.5/100 (C+)
```

---

## 📖 详细使用指南

### 🔧 scan 命令 — 项目扫描

`scan` 是 FrameScore 的核心命令，用于对前端项目进行全面扫描和评分。

```bash
# 基本扫描
framescore scan <path>

# 指定输出格式
framescore scan <path> --format json       # JSON 格式输出
framescore scan <path> --format markdown   # Markdown 报告
framescore scan <path> --format table      # 表格格式（默认）

# 指定前端框架
framescore scan <path> --framework react    # React 项目
framescore scan <path> --framework vue      # Vue 项目
framescore scan <path> --framework svelte   # Svelte 项目
framescore scan <path> --framework angular  # Angular 项目
framescore scan <path> --framework auto     # 自动检测（默认）

# 按严重程度过滤
framescore scan <path> --severity error     # 仅显示错误
framescore scan <path> --severity warning   # 显示错误和警告
framescore scan <path> --severity info      # 显示全部（默认）

# 保存报告到文件
framescore scan <path> --output report.md
framescore scan <path> --output report.json
framescore scan <path> -o result.md

# 跳过可选分析
framescore scan <path> --no-deps            # 跳过依赖分析
framescore scan <path> --no-git             # 跳过 Git 集成

# 性能调优
framescore scan <path> --workers 8          # 使用 8 个并行工作线程
framescore scan <path> --no-progress        # 禁用进度条

# 组合使用
framescore scan ./my-react-app --framework react --format json --severity warning -o report.json
```

### 📜 history 命令 — 评分历史

查看项目在 Git 提交历史中的评分变化趋势。

```bash
# 查看评分历史
framescore history <path>

# 示例输出
#   Date                 Commit     Score    Grade   Issues
#   ----------------------------------------------------------
#   2024-01-15 10:30:22  a1b2c3d     82.3      B      18
#   2024-01-14 16:45:10  e4f5g6h     79.1      C+     23
#   2024-01-13 09:12:05  i7j8k9l     85.6      B+     15
#
#   Trend: +3.2 (vs previous scan)
```

### 📚 rules 命令 — 规则列表

查看所有可用的分析规则。

```bash
# 列出所有规则
framescore rules

# 按框架过滤
framescore rules --framework react
framescore rules --framework vue
framescore rules --framework svelte
framescore rules --framework angular
framescore rules --framework general

# 按类别过滤
framescore rules --category security
framescore rules --category performance
framescore rules --category correctness
framescore rules --category best-practice
framescore rules --category accessibility
```

### ⚙️ 完整参数参考

| 参数 | 缩写 | 说明 | 默认值 |
|------|------|------|--------|
| `--format` | `-f` | 输出格式：table / json / markdown | table |
| `--framework` | | 框架选择：react / vue / svelte / angular / auto | auto |
| `--severity` | | 最低严重级别：error / warning / info | info |
| `--output` | `-o` | 报告输出文件路径 | - |
| `--workers` | `-w` | 并行工作线程数 | 4 |
| `--no-deps` | | 跳过依赖分析 | false |
| `--no-git` | | 跳过 Git 集成 | false |
| `--no-progress` | | 禁用进度条显示 | false |
| `-v` / `--version` | | 显示版本号 | - |

---

## 📊 评分体系

### 🧮 计算方式

FrameScore 采用**基准分扣减制**进行评分：

- **初始分数**：100 分
- 每发现一个 **Error（错误）** 级别问题：**-5 分**
- 每发现一个 **Warning（警告）** 级别问题：**-2 分**
- 每发现一个 **Info（提示）** 级别问题：**-0.5 分**
- 最终分数不低于 **0 分**

### 📈 等级划分

| 等级 | 分数范围 | 颜色标识 | 说明 |
|------|----------|----------|------|
| **A+** | 95 - 100 | 🟢 优秀 | 代码质量卓越，几乎无问题 |
| **A** | 90 - 94 | 🟢 良好 | 代码质量很高，仅有少量提示 |
| **B+** | 85 - 89 | 🔵 较好 | 代码质量较好，存在少量可改进项 |
| **B** | 80 - 84 | 🔵 中上 | 代码质量中等偏上，有一定改进空间 |
| **C+** | 75 - 79 | 🟡 中等 | 代码质量中等，需要关注部分问题 |
| **C** | 70 - 74 | 🟡 中下 | 代码质量一般，建议尽快修复警告 |
| **D** | 60 - 69 | 🔴 较差 | 代码质量较差，存在较多问题 |
| **F** | < 60 | 🔴 不及格 | 代码质量堪忧，需要全面重构 |

### 🏷️ 严重程度说明

| 级别 | 说明 | 示例 |
|------|------|------|
| 🔴 **Error** | 严重问题，可能导致 Bug 或安全漏洞 | 缺少 key 属性、eval() 使用、XSS 风险 |
| 🟡 **Warning** | 潜在问题，建议修复 | useEffect 缺少依赖数组、深层嵌套 |
| 🔵 **Info** | 代码改进建议 | 缺少注释、命名不规范、console 语句 |

---

## 🔍 规则列表

FrameScore 内置 **76 条规则**，覆盖 7 大类别。以下为完整规则清单：

### ⚛️ React 规则（15 条）

| 规则 ID | 名称 | 严重程度 | 类别 |
|---------|------|----------|------|
| REACT-001 | 列表渲染缺少 key 属性 | 🔴 Error | 正确性 |
| REACT-002 | useEffect 缺少依赖数组 | 🟡 Warning | 正确性 |
| REACT-003 | 直接 DOM 操作 | 🟡 Warning | 最佳实践 |
| REACT-004 | 缺少错误边界（Error Boundary） | 🔵 Info | 最佳实践 |
| REACT-005 | 动态列表使用 index 作为 key | 🟡 Warning | 正确性 |
| REACT-006 | useState 对象更新方式不当 | 🟡 Warning | 正确性 |
| REACT-007 | useEffect 缺少清理函数 | 🟡 Warning | 正确性 |
| REACT-008 | JSX 属性中的内联函数 | 🔵 Info | 性能 |
| REACT-009 | TypeScript 中使用 any 类型 | 🟡 Warning | 正确性 |
| REACT-010 | 缺少 PropTypes 或 TypeScript 类型定义 | 🔵 Info | 最佳实践 |
| REACT-011 | 对象/数组属性导致不必要重渲染 | 🔵 Info | 性能 |
| REACT-012 | 使用 dangerouslySetInnerHTML | 🔴 Error | 安全 |
| REACT-013 | img 标签缺少 alt 属性 | 🟡 Warning | 无障碍 |
| REACT-014 | 未使用的 import 语句 | 🔵 Info | 最佳实践 |
| REACT-015 | 生产代码中的 console 语句 | 🔵 Info | 最佳实践 |

### 💚 Vue 规则（10 条）

| 规则 ID | 名称 | 严重程度 | 类别 |
|---------|------|----------|------|
| VUE-001 | v-for 指令缺少 :key 属性 | 🔴 Error | 正确性 |
| VUE-002 | 同一元素同时使用 v-if 和 v-for | 🟡 Warning | 最佳实践 |
| VUE-003 | 未使用的组件导入 | 🔵 Info | 最佳实践 |
| VUE-004 | 缺少 prop 类型验证 | 🔵 Info | 最佳实践 |
| VUE-005 | 直接修改 props | 🔴 Error | 正确性 |
| VUE-006 | 过度使用 $refs | 🟡 Warning | 最佳实践 |
| VUE-007 | 异步方法缺少错误处理 | 🟡 Warning | 正确性 |
| VUE-008 | 生产代码中的 console 语句 | 🔵 Info | 最佳实践 |
| VUE-009 | 不必要的深度监听器 | 🔵 Info | 性能 |
| VUE-010 | Transition 组件内缺少 key | 🟡 Warning | 正确性 |

### 🧡 Svelte 规则（8 条）

| 规则 ID | 名称 | 严重程度 | 类别 |
|---------|------|----------|------|
| SVELTE-001 | {#each} 块缺少 key 表达式 | 🔴 Error | 正确性 |
| SVELTE-002 | 未使用的变量 | 🔵 Info | 最佳实践 |
| SVELTE-003 | Store 访问缺少 $ 前缀 | 🟡 Warning | 正确性 |
| SVELTE-004 | 生产代码中的 console 语句 | 🔵 Info | 最佳实践 |
| SVELTE-005 | 不必要的响应式声明 | 🔵 Info | 最佳实践 |
| SVELTE-006 | TypeScript 组件缺少类型注解 | 🔵 Info | 最佳实践 |
| SVELTE-007 | 无障碍问题（缺少 ARIA 标签） | 🟡 Warning | 无障碍 |
| SVELTE-008 | 组件文件过大 | 🟡 Warning | 最佳实践 |

### 🔴 Angular 规则（8 条）

| 规则 ID | 名称 | 严重程度 | 类别 |
|---------|------|----------|------|
| ANGULAR-001 | *ngFor 缺少 trackBy 函数 | 🟡 Warning | 性能 |
| ANGULAR-002 | TypeScript 中使用 any 类型 | 🟡 Warning | 正确性 |
| ANGULAR-003 | 生产代码中的 console 语句 | 🔵 Info | 最佳实践 |
| ANGULAR-004 | 未使用的 import 语句 | 🔵 Info | 最佳实践 |
| ANGULAR-005 | 缺少 OnPush 变更检测策略 | 🔵 Info | 性能 |
| ANGULAR-006 | 直接 DOM 访问 | 🟡 Warning | 最佳实践 |
| ANGULAR-007 | Observable 订阅缺少取消订阅 | 🟡 Warning | 正确性 |
| ANGULAR-008 | 组件文件过大 | 🟡 Warning | 最佳实践 |

### 📋 通用规则（15 条）

| 规则 ID | 名称 | 严重程度 | 类别 |
|---------|------|----------|------|
| GEN-001 | 文件过长（超过 500 行） | 🟡 Warning | 最佳实践 |
| GEN-002 | 函数过于复杂（超过 50 行） | 🟡 Warning | 最佳实践 |
| GEN-003 | 缺少文件头注释 | 🔵 Info | 最佳实践 |
| GEN-004 | 命名规范不一致 | 🔵 Info | 最佳实践 |
| GEN-005 | TODO/FIXME/HACK 注释 | 🔵 Info | 最佳实践 |
| GEN-006 | 死代码（未使用的导出） | 🔵 Info | 最佳实践 |
| GEN-007 | 重复代码块 | 🟡 Warning | 最佳实践 |
| GEN-008 | 缺少错误处理 | 🟡 Warning | 正确性 |
| GEN-009 | 硬编码字符串 | 🔵 Info | 最佳实践 |
| GEN-010 | 缺少函数注释 | 🔵 Info | 最佳实践 |
| GEN-011 | 代码嵌套过深 | 🟡 Warning | 最佳实践 |
| GEN-012 | 魔法数字 | 🔵 Info | 最佳实践 |
| GEN-013 | 函数参数过多（超过 5 个） | 🟡 Warning | 最佳实践 |
| GEN-014 | TypeScript 缺少返回类型注解 | 🔵 Info | 最佳实践 |
| GEN-015 | 文件命名不一致 | 🔵 Info | 最佳实践 |

### 🔒 安全规则（10 条）

| 规则 ID | 名称 | 严重程度 | 类别 |
|---------|------|----------|------|
| SEC-001 | eval() 使用 | 🔴 Error | 安全 |
| SEC-002 | innerHTML 赋值 | 🔴 Error | 安全 |
| SEC-003 | 硬编码密钥/API 密钥 | 🔴 Error | 安全 |
| SEC-004 | 使用 http:// 而非 https:// | 🟡 Warning | 安全 |
| SEC-005 | SQL 注入模式 | 🔴 Error | 安全 |
| SEC-006 | 路径遍历模式 | 🔴 Error | 安全 |
| SEC-007 | 命令注入模式 | 🔴 Error | 安全 |
| SEC-008 | 不安全的随机数生成 | 🟡 Warning | 安全 |
| SEC-009 | CORS 通配符配置 | 🟡 Warning | 安全 |
| SEC-010 | localStorage 存储敏感数据 | 🟡 Warning | 安全 |

### ⚡ 性能规则（10 条）

| 规则 ID | 名称 | 严重程度 | 类别 |
|---------|------|----------|------|
| PERF-001 | 大型库整体导入 | 🟡 Warning | 性能 |
| PERF-002 | 路由缺少懒加载 | 🔵 Info | 性能 |
| PERF-003 | 图片缺少 width/height 属性 | 🔵 Info | 性能 |
| PERF-004 | 同步文件操作 | 🟡 Warning | 性能 |
| PERF-005 | 不必要的重渲染模式 | 🔵 Info | 性能 |
| PERF-006 | 高频事件缺少防抖/节流 | 🔵 Info | 性能 |
| PERF-007 | 大型状态对象 | 🟡 Warning | 性能 |
| PERF-008 | 未优化的嵌套循环 | 🟡 Warning | 性能 |
| PERF-009 | 内存泄漏模式（事件监听器未清理） | 🟡 Warning | 性能 |
| PERF-010 | 大列表缺少虚拟化 | 🔵 Info | 性能 |

---

## 💡 设计思路与迭代规划

### 🎨 设计哲学

FrameScore 的设计遵循以下核心原则：

1. **零依赖原则** — 仅使用 Python 标准库，确保安装简单、运行稳定、无版本冲突
2. **约定优于配置** — 开箱即用，自动检测框架类型，无需繁琐的配置文件
3. **渐进式反馈** — 通过 Error / Warning / Info 三级严重程度，帮助开发者优先处理最关键的问题
4. **可量化度量** — 将代码质量转化为直观的分数和等级，便于团队沟通和追踪
5. **多框架平等** — 对 React、Vue、Svelte、Angular 一视同仁，提供同等深度的分析

### 🛠️ 技术选型

| 决策 | 选择 | 原因 |
|------|------|------|
| 实现语言 | Python | 丰富的文本处理能力，跨平台兼容性好 |
| 依赖管理 | 零外部依赖 | 降低安装门槛，避免版本冲突 |
| 并行策略 | 多线程（concurrent.futures） | I/O 密集型任务，多线程即可满足需求 |
| 规则引擎 | 基于正则表达式的模式匹配 | 轻量高效，无需 AST 解析器的复杂依赖 |
| 输出格式 | JSON / 表格 / Markdown | 覆盖 CI/CD 集成、终端查看、文档归档三大场景 |

### 🗺️ 迭代规划

#### v1.x — 稳定与完善
- [ ] 支持自定义规则配置文件（`.framescorerc`）
- [ ] 增加更多框架特定规则
- [ ] 支持 Web Components 框架
- [ ] 添加 HTML/CSS 分析规则

#### v2.0 — 智能化升级
- [ ] 基于 AST 的深度代码分析
- [ ] AI 辅助的修复建议
- [ ] 代码异味（Code Smell）检测
- [ ] 与主流 IDE 插件集成

#### v3.0 — 平台化
- [ ] Web 可视化仪表盘
- [ ] 团队协作与代码质量对比
- [ ] 历史趋势分析与预测
- [ ] GitHub App / GitLab CI 集成

---

## 📦 安装与部署

### 📥 安装方式

```bash
# 方式一：从 PyPI 安装（推荐）
pip install framescore

# 方式二：从 GitHub 安装最新开发版
pip install git+https://github.com/gitstq/FrameScore.git

# 方式三：从源码安装
git clone https://github.com/gitstq/FrameScore.git
cd FrameScore
pip install .
```

### 🐍 Python 版本支持

| Python 版本 | 支持状态 |
|-------------|----------|
| 3.12 | ✅ 支持 |
| 3.11 | ✅ 支持 |
| 3.10 | ✅ 支持 |
| 3.9 | ✅ 支持 |
| 3.8 | ✅ 支持 |
| < 3.8 | ❌ 不支持 |

### 🔄 CI/CD 集成

在 CI/CD 流水线中使用 FrameScore，实现自动化代码质量检查：

**GitHub Actions 示例：**

```yaml
name: Code Health Check

on: [push, pull_request]

jobs:
  framescore:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install FrameScore
        run: pip install framescore
      - name: Run FrameScore
        run: framescore scan . --format json --output report.json --severity warning
      - name: Check Score
        run: |
          SCORE=$(python -c "import json; print(json.load(open('report.json'))['health']['overall_score'])")
          if (( $(echo "$SCORE < 70" | bc -l) )); then
            echo "Score $SCORE is below threshold 70"
            exit 1
          fi
```

**GitLab CI 示例：**

```yaml
code_health:
  stage: test
  image: python:3.11
  script:
    - pip install framescore
    - framescore scan . --format json --output report.json --severity warning
  artifacts:
    paths:
      - report.json
```

---

## 🤝 贡献指南

我们欢迎并感谢每一位贡献者！以下是参与贡献的指南：

### 📌 贡献流程

1. **Fork** 本仓库到你的 GitHub 账号
2. **Clone** 你 fork 的仓库到本地
3. **创建分支**：`git checkout -b feature/your-feature-name`
4. **开发与测试**：编写代码并确保通过所有测试
5. **提交代码**：`git commit -m "feat: add your feature description"`
6. **推送分支**：`git push origin feature/your-feature-name`
7. **发起 Pull Request**：在 GitHub 上创建 PR 并描述你的改动

### 📝 提交规范

请遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat:` 新功能
- `fix:` 修复 Bug
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具链相关

### 🐛 提交 Issue

提交 Issue 时，请包含以下信息：

- **问题描述** — 清晰描述你遇到的问题或建议
- **复现步骤** — 如何复现该问题（如果是 Bug）
- **期望行为** — 你期望的正确行为是什么
- **环境信息** — Python 版本、操作系统、框架版本等
- **截图/日志** — 如有可能，附上相关截图或错误日志

### ✅ 行为准则

- 尊重所有贡献者
- 接受建设性的代码审查意见
- 保持代码风格一致
- 为新功能编写对应的测试用例
- 更新相关文档

---

## 📄 开源协议

FrameScore 基于 [MIT License](https://opensource.org/licenses/MIT) 开源。

```
MIT License

Copyright (c) 2024 FrameScore Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">
  Made with ❤️ by <strong>FrameScore Team</strong><br/>
  如果你觉得 FrameScore 对你有帮助，请给项目点一个 ⭐ Star！
</p>

---
---

<a id="繁體中文"></a>

# 🇹🇼 繁體中文

---

## 🎉 專案介紹

FrameScore 是一款專為前端開發者打造的**輕量級程式碼健康智慧評分引擎**。它能夠深入掃描你的前端專案，基於 **76 條內建規則**對程式碼品質進行全面體檢，最終輸出一個直觀的 **0-100 健康評分**及 **A+ 到 F 等級評定**。

### 💡 為什麼需要 FrameScore？

在日常前端開發中，我們常常面臨以下痛點：

- **程式碼審查耗時耗力** — 人工逐行檢查程式碼規範和潛在問題，效率低落
- **缺少統一的品質度量** — 團隊對「好程式碼」缺乏可量化的標準
- **框架最佳實踐難以落實** — React、Vue、Svelte、Angular 各有最佳實踐，但難以全面覆蓋
- **安全漏洞容易被忽視** — XSS、注入攻擊等安全隱患在日常開發中屢見不鮮
- **效能問題難以定位** — 不必要的重渲染、記憶體洩漏等問題隱藏在程式碼深處

### 🌟 核心差異化優勢

- **零外部依賴** — 純 Python 標準函式庫實作，安裝即用，無需配置複雜環境
- **多框架支援** — 一站式覆蓋 React、Vue、Svelte、Angular 四大主流框架
- **智慧評分體系** — 科學加權演算法，將複雜的程式碼分析結果轉化為直觀的 0-100 分數
- **平行分析引擎** — 多執行緒平行掃描，大型專案也能快速完成分析
- **Git 歷史追蹤** — 自動記錄每次評分，追蹤程式碼品質變化趨勢
- **靈活輸出格式** — 支援 JSON、表格、Markdown 三種輸出格式，方便整合到 CI/CD

### 🎯 靈感來源

FrameScore 的靈感來源於程式碼品質評分工具（如 Code Climate、SonarQube）的理念，但專注於前端框架特有的程式碼模式和最佳實踐。我們希望為前端團隊提供一個**開箱即用、零配置、輕量高效**的程式碼健康評估方案。

---

## ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🏥 **智慧健康評分** | 基於 76 條規則的綜合評分，0-100 分直觀反映程式碼健康狀態 |
| 📊 **A+ 到 F 等級** | 科學的等級劃分，快速了解專案品質水準 |
| ⚡ **平行分析引擎** | 多執行緒平行掃描，大幅提升大型專案分析速度 |
| 🔍 **76 條內建規則** | 覆蓋 React、Vue、Svelte、Angular 及通用、安全、效能六大類別 |
| 📦 **依賴分析** | 自動偵測專案依賴，識別缺失鎖定檔案和非語義化版本 |
| 🔗 **Git 整合** | 自動追蹤評分歷史，視覺化程式碼品質變化趨勢 |
| 📋 **多種輸出格式** | 支援 JSON、表格、Markdown 三種格式，滿足不同使用場景 |
| 🎯 **框架自動偵測** | 智慧識別專案使用的框架，自動載入對應規則集 |
| 🚫 **零外部依賴** | 純 Python 標準函式庫實作，安裝即用無負擔 |
| ⚙️ **靈活配置** | 支援按嚴重程度過濾、指定框架、自訂工作執行緒數等 |

---

## 🚀 快速開始

### 📋 環境需求

- **Python** 3.8 或更高版本
- 無需安裝任何第三方依賴

### 📦 安裝

```bash
# 從 PyPI 安裝（推薦）
pip install framescore

# 從 GitHub 安裝最新版本
pip install git+https://github.com/gitstq/FrameScore.git
```

### 🏃 快速執行

```bash
# 掃描目前目錄
framescore scan .

# 掃描指定專案
framescore scan /path/to/your/project

# 查看版本資訊
framescore -v
```

### 📸 輸出範例

掃描完成後，你將看到類似以下的輸出：

```
  ╔══════════════════════════════════════╗
  ║         FrameScore v1.0.0           ║
  ║   Code Health Scoring Engine        ║
  ╚══════════════════════════════════════╝

  Scanning project...
  Framework:  react
  Files:      42 (3,856 lines)
  Deps:       28 (18 prod, 10 dev)
  Branch:     main
  Commits:    156

  Completed in 2.3s | 23 issues found | Score: 78.5/100 (C+)
```

---

## 📖 詳細使用指南

### 🔧 scan 指令 — 專案掃描

`scan` 是 FrameScore 的核心指令，用於對前端專案進行全面掃描和評分。

```bash
# 基本掃描
framescore scan <path>

# 指定輸出格式
framescore scan <path> --format json       # JSON 格式輸出
framescore scan <path> --format markdown   # Markdown 報告
framescore scan <path> --format table      # 表格格式（預設）

# 指定前端框架
framescore scan <path> --framework react    # React 專案
framescore scan <path> --framework vue      # Vue 專案
framescore scan <path> --framework svelte   # Svelte 專案
framescore scan <path> --framework angular  # Angular 專案
framescore scan <path> --framework auto     # 自動偵測（預設）

# 按嚴重程度過濾
framescore scan <path> --severity error     # 僅顯示錯誤
framescore scan <path> --severity warning   # 顯示錯誤和警告
framescore scan <path> --severity info      # 顯示全部（預設）

# 儲存報告到檔案
framescore scan <path> --output report.md
framescore scan <path> --output report.json
framescore scan <path> -o result.md

# 跳過可選分析
framescore scan <path> --no-deps            # 跳過依賴分析
framescore scan <path> --no-git             # 跳過 Git 整合

# 效能調校
framescore scan <path> --workers 8          # 使用 8 個平行工作執行緒
framescore scan <path> --no-progress        # 停用進度條

# 組合使用
framescore scan ./my-react-app --framework react --format json --severity warning -o report.json
```

### 📜 history 指令 — 評分歷史

查看專案在 Git 提交歷史中的評分變化趨勢。

```bash
# 查看評分歷史
framescore history <path>

# 範例輸出
#   Date                 Commit     Score    Grade   Issues
#   ----------------------------------------------------------
#   2024-01-15 10:30:22  a1b2c3d     82.3      B      18
#   2024-01-14 16:45:10  e4f5g6h     79.1      C+     23
#   2024-01-13 09:12:05  i7j8k9l     85.6      B+     15
#
#   Trend: +3.2 (vs previous scan)
```

### 📚 rules 指令 — 規則清單

查看所有可用的分析規則。

```bash
# 列出所有規則
framescore rules

# 按框架過濾
framescore rules --framework react
framescore rules --framework vue
framescore rules --framework svelte
framescore rules --framework angular
framescore rules --framework general

# 按類別過濾
framescore rules --category security
framescore rules --category performance
framescore rules --category correctness
framescore rules --category best-practice
framescore rules --category accessibility
```

### ⚙️ 完整參數參考

| 參數 | 縮寫 | 說明 | 預設值 |
|------|------|------|--------|
| `--format` | `-f` | 輸出格式：table / json / markdown | table |
| `--framework` | | 框架選擇：react / vue / svelte / angular / auto | auto |
| `--severity` | | 最低嚴重級別：error / warning / info | info |
| `--output` | `-o` | 報告輸出檔案路徑 | - |
| `--workers` | `-w` | 平行工作執行緒數 | 4 |
| `--no-deps` | | 跳過依賴分析 | false |
| `--no-git` | | 跳過 Git 整合 | false |
| `--no-progress` | | 停用進度條顯示 | false |
| `-v` / `--version` | | 顯示版本號 | - |

---

## 📊 評分體系

### 🧮 計算方式

FrameScore 採用**基準分扣減制**進行評分：

- **初始分數**：100 分
- 每發現一個 **Error（錯誤）** 級別問題：**-5 分**
- 每發現一個 **Warning（警告）** 級別問題：**-2 分**
- 每發現一個 **Info（提示）** 級別問題：**-0.5 分**
- 最終分數不低於 **0 分**

### 📈 等級劃分

| 等級 | 分數範圍 | 顏色標識 | 說明 |
|------|----------|----------|------|
| **A+** | 95 - 100 | 🟢 優秀 | 程式碼品質卓越，幾乎無問題 |
| **A** | 90 - 94 | 🟢 良好 | 程式碼品質很高，僅有少量提示 |
| **B+** | 85 - 89 | 🔵 較好 | 程式碼品質較好，存在少量可改進項 |
| **B** | 80 - 84 | 🔵 中上 | 程式碼品質中等偏上，有一定改進空間 |
| **C+** | 75 - 79 | 🟡 中等 | 程式碼品質中等，需要關注部分問題 |
| **C** | 70 - 74 | 🟡 中下 | 程式碼品質一般，建議盡快修復警告 |
| **D** | 60 - 69 | 🔴 較差 | 程式碼品質較差，存在較多問題 |
| **F** | < 60 | 🔴 不及格 | 程式碼品質堪慮，需要全面重構 |

### 🏷️ 嚴重程度說明

| 級別 | 說明 | 範例 |
|------|------|------|
| 🔴 **Error** | 嚴重問題，可能導致 Bug 或安全漏洞 | 缺少 key 屬性、eval() 使用、XSS 風險 |
| 🟡 **Warning** | 潛在問題，建議修復 | useEffect 缺少依賴陣列、深層巢狀 |
| 🔵 **Info** | 程式碼改進建議 | 缺少註解、命名不規範、console 陳述式 |

---

## 🔍 規則清單

FrameScore 內建 **76 條規則**，覆蓋 7 大類別。以下為完整規則清單：

### ⚛️ React 規則（15 條）

| 規則 ID | 名稱 | 嚴重程度 | 類別 |
|---------|------|----------|------|
| REACT-001 | 列表渲染缺少 key 屬性 | 🔴 Error | 正確性 |
| REACT-002 | useEffect 缺少依賴陣列 | 🟡 Warning | 正確性 |
| REACT-003 | 直接 DOM 操作 | 🟡 Warning | 最佳實踐 |
| REACT-004 | 缺少錯誤邊界（Error Boundary） | 🔵 Info | 最佳實踐 |
| REACT-005 | 動態列表使用 index 作為 key | 🟡 Warning | 正確性 |
| REACT-006 | useState 物件更新方式不當 | 🟡 Warning | 正確性 |
| REACT-007 | useEffect 缺少清理函式 | 🟡 Warning | 正確性 |
| REACT-008 | JSX 屬性中的內聯函式 | 🔵 Info | 效能 |
| REACT-009 | TypeScript 中使用 any 類型 | 🟡 Warning | 正確性 |
| REACT-010 | 缺少 PropTypes 或 TypeScript 類型定義 | 🔵 Info | 最佳實踐 |
| REACT-011 | 物件/陣列屬性導致不必要的重渲染 | 🔵 Info | 效能 |
| REACT-012 | 使用 dangerouslySetInnerHTML | 🔴 Error | 安全 |
| REACT-013 | img 標籤缺少 alt 屬性 | 🟡 Warning | 無障礙 |
| REACT-014 | 未使用的 import 陳述式 | 🔵 Info | 最佳實踐 |
| REACT-015 | 生產程式碼中的 console 陳述式 | 🔵 Info | 最佳實踐 |

### 💚 Vue 規則（10 條）

| 規則 ID | 名稱 | 嚴重程度 | 類別 |
|---------|------|----------|------|
| VUE-001 | v-for 指令缺少 :key 屬性 | 🔴 Error | 正確性 |
| VUE-002 | 同一元素同時使用 v-if 和 v-for | 🟡 Warning | 最佳實踐 |
| VUE-003 | 未使用的元件匯入 | 🔵 Info | 最佳實踐 |
| VUE-004 | 缺少 prop 類型驗證 | 🔵 Info | 最佳實踐 |
| VUE-005 | 直接修改 props | 🔴 Error | 正確性 |
| VUE-006 | 過度使用 $refs | 🟡 Warning | 最佳實踐 |
| VUE-007 | 非同步方法缺少錯誤處理 | 🟡 Warning | 正確性 |
| VUE-008 | 生產程式碼中的 console 陳述式 | 🔵 Info | 最佳實踐 |
| VUE-009 | 不必要的深度監聽器 | 🔵 Info | 效能 |
| VUE-010 | Transition 元件內缺少 key | 🟡 Warning | 正確性 |

### 🧡 Svelte 規則（8 條）

| 規則 ID | 名稱 | 嚴重程度 | 類別 |
|---------|------|----------|------|
| SVELTE-001 | {#each} 區塊缺少 key 運算式 | 🔴 Error | 正確性 |
| SVELTE-002 | 未使用的變數 | 🔵 Info | 最佳實踐 |
| SVELTE-003 | Store 存取缺少 $ 前綴 | 🟡 Warning | 正確性 |
| SVELTE-004 | 生產程式碼中的 console 陳述式 | 🔵 Info | 最佳實踐 |
| SVELTE-005 | 不必要的響應式宣告 | 🔵 Info | 最佳實踐 |
| SVELTE-006 | TypeScript 元件缺少類型註解 | 🔵 Info | 最佳實踐 |
| SVELTE-007 | 無障礙問題（缺少 ARIA 標籤） | 🟡 Warning | 無障礙 |
| SVELTE-008 | 元件檔案過大 | 🟡 Warning | 最佳實踐 |

### 🔴 Angular 規則（8 條）

| 規則 ID | 名稱 | 嚴重程度 | 類別 |
|---------|------|----------|------|
| ANGULAR-001 | *ngFor 缺少 trackBy 函式 | 🟡 Warning | 效能 |
| ANGULAR-002 | TypeScript 中使用 any 類型 | 🟡 Warning | 正確性 |
| ANGULAR-003 | 生產程式碼中的 console 陳述式 | 🔵 Info | 最佳實踐 |
| ANGULAR-004 | 未使用的 import 陳述式 | 🔵 Info | 最佳實踐 |
| ANGULAR-005 | 缺少 OnPush 變更偵測策略 | 🔵 Info | 效能 |
| ANGULAR-006 | 直接 DOM 存取 | 🟡 Warning | 最佳實踐 |
| ANGULAR-007 | Observable 訂閱缺少取消訂閱 | 🟡 Warning | 正確性 |
| ANGULAR-008 | 元件檔案過大 | 🟡 Warning | 最佳實踐 |

### 📋 通用規則（15 條）

| 規則 ID | 名稱 | 嚴重程度 | 類別 |
|---------|------|----------|------|
| GEN-001 | 檔案過長（超過 500 行） | 🟡 Warning | 最佳實踐 |
| GEN-002 | 函式過於複雜（超過 50 行） | 🟡 Warning | 最佳實踐 |
| GEN-003 | 缺少檔案頭註解 | 🔵 Info | 最佳實踐 |
| GEN-004 | 命名規範不一致 | 🔵 Info | 最佳實踐 |
| GEN-005 | TODO/FIXME/HACK 註解 | 🔵 Info | 最佳實踐 |
| GEN-006 | 死程式碼（未使用的匯出） | 🔵 Info | 最佳實踐 |
| GEN-007 | 重複程式碼區塊 | 🟡 Warning | 最佳實踐 |
| GEN-008 | 缺少錯誤處理 | 🟡 Warning | 正確性 |
| GEN-009 | 硬編碼字串 | 🔵 Info | 最佳實踐 |
| GEN-010 | 缺少函式註解 | 🔵 Info | 最佳實踐 |
| GEN-011 | 程式碼巢狀過深 | 🟡 Warning | 最佳實踐 |
| GEN-012 | 魔法數字 | 🔵 Info | 最佳實踐 |
| GEN-013 | 函式參數過多（超過 5 個） | 🟡 Warning | 最佳實踐 |
| GEN-014 | TypeScript 缺少回傳類型註解 | 🔵 Info | 最佳實踐 |
| GEN-015 | 檔案命名不一致 | 🔵 Info | 最佳實踐 |

### 🔒 安全規則（10 條）

| 規則 ID | 名稱 | 嚴重程度 | 類別 |
|---------|------|----------|------|
| SEC-001 | eval() 使用 | 🔴 Error | 安全 |
| SEC-002 | innerHTML 賦值 | 🔴 Error | 安全 |
| SEC-003 | 硬編碼密鑰/API 金鑰 | 🔴 Error | 安全 |
| SEC-004 | 使用 http:// 而非 https:// | 🟡 Warning | 安全 |
| SEC-005 | SQL 注入模式 | 🔴 Error | 安全 |
| SEC-006 | 路徑遍歷模式 | 🔴 Error | 安全 |
| SEC-007 | 命令注入模式 | 🔴 Error | 安全 |
| SEC-008 | 不安全的隨機數生成 | 🟡 Warning | 安全 |
| SEC-009 | CORS 萬用字元配置 | 🟡 Warning | 安全 |
| SEC-010 | localStorage 儲存敏感資料 | 🟡 Warning | 安全 |

### ⚡ 效能規則（10 條）

| 規則 ID | 名稱 | 嚴重程度 | 類別 |
|---------|------|----------|------|
| PERF-001 | 大型函式庫整體匯入 | 🟡 Warning | 效能 |
| PERF-002 | 路由缺少懶載入 | 🔵 Info | 效能 |
| PERF-003 | 圖片缺少 width/height 屬性 | 🔵 Info | 效能 |
| PERF-004 | 同步檔案操作 | 🟡 Warning | 效能 |
| PERF-005 | 不必要的重渲染模式 | 🔵 Info | 效能 |
| PERF-006 | 高頻事件缺少防抖/節流 | 🔵 Info | 效能 |
| PERF-007 | 大型狀態物件 | 🟡 Warning | 效能 |
| PERF-008 | 未最佳化的巢狀迴圈 | 🟡 Warning | 效能 |
| PERF-009 | 記憶體洩漏模式（事件監聽器未清理） | 🟡 Warning | 效能 |
| PERF-010 | 大列表缺少虛擬化 | 🔵 Info | 效能 |

---

## 💡 設計思路與迭代規劃

### 🎨 設計哲學

FrameScore 的設計遵循以下核心原則：

1. **零依賴原則** — 僅使用 Python 標準函式庫，確保安裝簡單、執行穩定、無版本衝突
2. **約定優於配置** — 開箱即用，自動偵測框架類型，無需繁瑣的配置檔案
3. **漸進式回饋** — 透過 Error / Warning / Info 三級嚴重程度，幫助開發者優先處理最關鍵的問題
4. **可量化度量** — 將程式碼品質轉化為直觀的分數和等級，便於團隊溝通和追蹤
5. **多框架平等** — 對 React、Vue、Svelte、Angular 一視同仁，提供同等深度的分析

### 🛠️ 技術選型

| 決策 | 選擇 | 原因 |
|------|------|------|
| 實作語言 | Python | 豐富的文字處理能力，跨平台相容性好 |
| 依賴管理 | 零外部依賴 | 降低安裝門檻，避免版本衝突 |
| 平行策略 | 多執行緒（concurrent.futures） | I/O 密集型任務，多執行緒即可滿足需求 |
| 規則引擎 | 基於正規表示式的模式比對 | 輕量高效，無需 AST 解析器的複雜依賴 |
| 輸出格式 | JSON / 表格 / Markdown | 覆蓋 CI/CD 整合、終端查看、文件歸檔三大場景 |

### 🗺️ 迭代規劃

#### v1.x — 穩定與完善
- [ ] 支援自訂規則配置檔案（`.framescorerc`）
- [ ] 增加更多框架特定規則
- [ ] 支援 Web Components 框架
- [ ] 新增 HTML/CSS 分析規則

#### v2.0 — 智慧化升級
- [ ] 基於 AST 的深度程式碼分析
- [ ] AI 輔助的修復建議
- [ ] 程式碼異味（Code Smell）偵測
- [ ] 與主流 IDE 外掛整合

#### v3.0 — 平台化
- [ ] Web 視覺化儀表板
- [ ] 團隊協作與程式碼品質對比
- [ ] 歷史趨勢分析與預測
- [ ] GitHub App / GitLab CI 整合

---

## 📦 安裝與部署

### 📥 安裝方式

```bash
# 方式一：從 PyPI 安裝（推薦）
pip install framescore

# 方式二：從 GitHub 安裝最新開發版
pip install git+https://github.com/gitstq/FrameScore.git

# 方式三：從原始碼安裝
git clone https://github.com/gitstq/FrameScore.git
cd FrameScore
pip install .
```

### 🐍 Python 版本支援

| Python 版本 | 支援狀態 |
|-------------|----------|
| 3.12 | ✅ 支援 |
| 3.11 | ✅ 支援 |
| 3.10 | ✅ 支援 |
| 3.9 | ✅ 支援 |
| 3.8 | ✅ 支援 |
| < 3.8 | ❌ 不支援 |

### 🔄 CI/CD 整合

在 CI/CD 流水線中使用 FrameScore，實現自動化程式碼品質檢查：

**GitHub Actions 範例：**

```yaml
name: Code Health Check

on: [push, pull_request]

jobs:
  framescore:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install FrameScore
        run: pip install framescore
      - name: Run FrameScore
        run: framescore scan . --format json --output report.json --severity warning
      - name: Check Score
        run: |
          SCORE=$(python -c "import json; print(json.load(open('report.json'))['health']['overall_score'])")
          if (( $(echo "$SCORE < 70" | bc -l) )); then
            echo "Score $SCORE is below threshold 70"
            exit 1
          fi
```

**GitLab CI 範例：**

```yaml
code_health:
  stage: test
  image: python:3.11
  script:
    - pip install framescore
    - framescore scan . --format json --output report.json --severity warning
  artifacts:
    paths:
      - report.json
```

---

## 🤝 貢獻指南

我們歡迎並感謝每一位貢獻者！以下是參與貢獻的指南：

### 📌 貢獻流程

1. **Fork** 本儲存庫到你的 GitHub 帳號
2. **Clone** 你 fork 的儲存庫到本機
3. **建立分支**：`git checkout -b feature/your-feature-name`
4. **開發與測試**：撰寫程式碼並確保通過所有測試
5. **提交程式碼**：`git commit -m "feat: add your feature description"`
6. **推送分支**：`git push origin feature/your-feature-name`
7. **發起 Pull Request**：在 GitHub 上建立 PR 並描述你的變更

### 📝 提交規範

請遵循 [Conventional Commits](https://www.conventionalcommits.org/) 規範：

- `feat:` 新功能
- `fix:` 修復 Bug
- `docs:` 文件更新
- `style:` 程式碼格式調整
- `refactor:` 程式碼重構
- `test:` 測試相關
- `chore:` 建置/工具鏈相關

### 🐛 提交 Issue

提交 Issue 時，請包含以下資訊：

- **問題描述** — 清晰描述你遇到的問題或建議
- **重現步驟** — 如何重現該問題（如果是 Bug）
- **期望行為** — 你期望的正確行為是什麼
- **環境資訊** — Python 版本、作業系統、框架版本等
- **截圖/日誌** — 如有可能，附上相關截圖或錯誤日誌

### ✅ 行為準則

- 尊重所有貢獻者
- 接受建設性的程式碼審查意見
- 保持程式碼風格一致
- 為新功能撰寫對應的測試案例
- 更新相關文件

---

## 📄 開源協議

FrameScore 基於 [MIT License](https://opensource.org/licenses/MIT) 開源。

```
MIT License

Copyright (c) 2024 FrameScore Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">
  Made with ❤️ by <strong>FrameScore Team</strong><br/>
  如果你覺得 FrameScore 對你有幫助，請給專案點一個 ⭐ Star！
</p>

---
---

<a id="english"></a>

# 🇬🇧 English

---

## 🎉 Introduction

FrameScore is a **lightweight code health intelligent scoring engine** designed specifically for frontend developers. It performs in-depth scans of your frontend projects, evaluates code quality based on **76 built-in rules**, and outputs an intuitive **0-100 health score** with an **A+ to F grade**.

### 💡 Why FrameScore?

In daily frontend development, we often face these pain points:

- **Code review is time-consuming** — Manually checking code standards and potential issues line by line is inefficient
- **Lack of unified quality metrics** — Teams lack quantifiable standards for "good code"
- **Framework best practices are hard to enforce** — React, Vue, Svelte, and Angular each have best practices, but covering them all comprehensively is challenging
- **Security vulnerabilities are easily overlooked** — XSS, injection attacks, and other security risks are common in daily development
- **Performance issues are hard to pinpoint** — Unnecessary re-renders, memory leaks, and other issues hide deep within the code

### 🌟 Key Differentiators

- **Zero external dependencies** — Built entirely with the Python standard library; install and run with no complex setup
- **Multi-framework support** — Comprehensive coverage of React, Vue, Svelte, and Angular in one tool
- **Intelligent scoring system** — Scientifically weighted algorithm that translates complex analysis results into an intuitive 0-100 score
- **Parallel analysis engine** — Multi-threaded parallel scanning for fast analysis even on large projects
- **Git history tracking** — Automatically records scores and tracks code quality trends over time
- **Flexible output formats** — Supports JSON, table, and Markdown output for seamless CI/CD integration

### 🎯 Inspiration

FrameScore was inspired by the philosophy of code quality scoring tools (such as Code Climate and SonarQube), but focuses specifically on frontend framework-specific code patterns and best practices. Our goal is to provide frontend teams with an **out-of-the-box, zero-config, lightweight, and efficient** code health assessment solution.

---

## ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🏥 **Intelligent Health Scoring** | Comprehensive scoring based on 76 rules, 0-100 score reflecting code health at a glance |
| 📊 **A+ to F Grading** | Scientific grade tiers for quick assessment of project quality |
| ⚡ **Parallel Analysis Engine** | Multi-threaded parallel scanning for significantly faster analysis on large projects |
| 🔍 **76 Built-in Rules** | Covering React, Vue, Svelte, Angular, plus general, security, and performance categories |
| 📦 **Dependency Analysis** | Automatically detects project dependencies, identifies missing lock files and non-semver versions |
| 🔗 **Git Integration** | Automatically tracks score history and visualizes code quality trends |
| 📋 **Multiple Output Formats** | JSON, table, and Markdown formats for different use cases |
| 🎯 **Auto Framework Detection** | Intelligently identifies the project's framework and loads the corresponding rule set |
| 🚫 **Zero External Dependencies** | Pure Python standard library implementation, install and run with no overhead |
| ⚙️ **Flexible Configuration** | Filter by severity, specify framework, customize worker thread count, and more |

---

## 🚀 Quick Start

### 📋 Requirements

- **Python** 3.8 or higher
- No third-party dependencies required

### 📦 Installation

```bash
# Install from PyPI (recommended)
pip install framescore

# Install latest version from GitHub
pip install git+https://github.com/gitstq/FrameScore.git
```

### 🏃 Quick Run

```bash
# Scan the current directory
framescore scan .

# Scan a specific project
framescore scan /path/to/your/project

# Check version info
framescore -v
```

### 📸 Output Example

After scanning, you will see output similar to this:

```
  ╔══════════════════════════════════════╗
  ║         FrameScore v1.0.0           ║
  ║   Code Health Scoring Engine        ║
  ╚══════════════════════════════════════╝

  Scanning project...
  Framework:  react
  Files:      42 (3,856 lines)
  Deps:       28 (18 prod, 10 dev)
  Branch:     main
  Commits:    156

  Completed in 2.3s | 23 issues found | Score: 78.5/100 (C+)
```

---

## 📖 Usage Guide

### 🔧 scan Command — Project Scanning

The `scan` command is the core of FrameScore, performing comprehensive scanning and scoring of frontend projects.

```bash
# Basic scan
framescore scan <path>

# Specify output format
framescore scan <path> --format json       # JSON output
framescore scan <path> --format markdown   # Markdown report
framescore scan <path> --format table      # Table format (default)

# Specify frontend framework
framescore scan <path> --framework react    # React project
framescore scan <path> --framework vue      # Vue project
framescore scan <path> --framework svelte   # Svelte project
framescore scan <path> --framework angular  # Angular project
framescore scan <path> --framework auto     # Auto-detect (default)

# Filter by severity level
framescore scan <path> --severity error     # Errors only
framescore scan <path> --severity warning   # Errors and warnings
framescore scan <path> --severity info      # All issues (default)

# Save report to file
framescore scan <path> --output report.md
framescore scan <path> --output report.json
framescore scan <path> -o result.md

# Skip optional analysis
framescore scan <path> --no-deps            # Skip dependency analysis
framescore scan <path> --no-git             # Skip Git integration

# Performance tuning
framescore scan <path> --workers 8          # Use 8 parallel worker threads
framescore scan <path> --no-progress        # Disable progress bar

# Combine options
framescore scan ./my-react-app --framework react --format json --severity warning -o report.json
```

### 📜 history Command — Score History

View score trends across Git commit history.

```bash
# View score history
framescore history <path>

# Example output
#   Date                 Commit     Score    Grade   Issues
#   ----------------------------------------------------------
#   2024-01-15 10:30:22  a1b2c3d     82.3      B      18
#   2024-01-14 16:45:10  e4f5g6h     79.1      C+     23
#   2024-01-13 09:12:05  i7j8k9l     85.6      B+     15
#
#   Trend: +3.2 (vs previous scan)
```

### 📚 rules Command — Rule Catalog

View all available analysis rules.

```bash
# List all rules
framescore rules

# Filter by framework
framescore rules --framework react
framescore rules --framework vue
framescore rules --framework svelte
framescore rules --framework angular
framescore rules --framework general

# Filter by category
framescore rules --category security
framescore rules --category performance
framescore rules --category correctness
framescore rules --category best-practice
framescore rules --category accessibility
```

### ⚙️ Full Parameter Reference

| Parameter | Short | Description | Default |
|-----------|-------|-------------|---------|
| `--format` | `-f` | Output format: table / json / markdown | table |
| `--framework` | | Framework: react / vue / svelte / angular / auto | auto |
| `--severity` | | Minimum severity: error / warning / info | info |
| `--output` | `-o` | Report output file path | - |
| `--workers` | `-w` | Number of parallel worker threads | 4 |
| `--no-deps` | | Skip dependency analysis | false |
| `--no-git` | | Skip Git integration | false |
| `--no-progress` | | Disable progress bar | false |
| `-v` / `--version` | | Show version number | - |

---

## 📊 Scoring System

### 🧮 Calculation Method

FrameScore uses a **base-score deduction** system:

- **Starting score**: 100 points
- Each **Error** level issue found: **-5 points**
- Each **Warning** level issue found: **-2 points**
- Each **Info** level issue found: **-0.5 points**
- Final score is never below **0 points**

### 📈 Grade Breakdown

| Grade | Score Range | Color | Description |
|-------|-------------|-------|-------------|
| **A+** | 95 - 100 | 🟢 Excellent | Outstanding code quality, virtually no issues |
| **A** | 90 - 94 | 🟢 Good | High code quality, only minor suggestions |
| **B+** | 85 - 89 | 🔵 Fair+ | Good code quality, a few areas for improvement |
| **B** | 80 - 84 | 🔵 Fair | Above-average code quality, some room for improvement |
| **C+** | 75 - 79 | 🟡 Average | Average code quality, some issues need attention |
| **C** | 70 - 74 | 🟡 Below Average | Below-average code quality, warnings should be addressed |
| **D** | 60 - 69 | 🔴 Poor | Poor code quality, many issues present |
| **F** | < 60 | 🔴 Failing | Critical code quality issues, comprehensive refactoring needed |

### 🏷️ Severity Levels

| Level | Description | Examples |
|-------|-------------|----------|
| 🔴 **Error** | Serious issues that may cause bugs or security vulnerabilities | Missing key prop, eval() usage, XSS risks |
| 🟡 **Warning** | Potential issues that should be fixed | useEffect missing dependency array, deep nesting |
| 🔵 **Info** | Code improvement suggestions | Missing comments, naming inconsistencies, console statements |

---

## 🔍 Rule Catalog

FrameScore includes **76 built-in rules** across 7 categories. Below is the complete rule listing:

### ⚛️ React Rules (15)

| Rule ID | Name | Severity | Category |
|---------|------|----------|----------|
| REACT-001 | Missing key prop in list rendering | 🔴 Error | Correctness |
| REACT-002 | useEffect missing dependency array | 🟡 Warning | Correctness |
| REACT-003 | Direct DOM manipulation | 🟡 Warning | Best Practice |
| REACT-004 | Missing error boundary | 🔵 Info | Best Practice |
| REACT-005 | Using index as key for dynamic lists | 🟡 Warning | Correctness |
| REACT-006 | useState object without proper update | 🟡 Warning | Correctness |
| REACT-007 | useEffect missing cleanup | 🟡 Warning | Correctness |
| REACT-008 | Inline function in JSX props | 🔵 Info | Performance |
| REACT-009 | Using 'any' type in TypeScript React | 🟡 Warning | Correctness |
| REACT-010 | Missing PropTypes or TypeScript types | 🔵 Info | Best Practice |
| REACT-011 | Unnecessary re-renders (object/array props) | 🔵 Info | Performance |
| REACT-012 | dangerouslySetInnerHTML usage | 🔴 Error | Security |
| REACT-013 | Missing alt prop on img tags | 🟡 Warning | Accessibility |
| REACT-014 | Unused imports | 🔵 Info | Best Practice |
| REACT-015 | Console statements in production code | 🔵 Info | Best Practice |

### 💚 Vue Rules (10)

| Rule ID | Name | Severity | Category |
|---------|------|----------|----------|
| VUE-001 | Missing key in v-for | 🔴 Error | Correctness |
| VUE-002 | v-if and v-for on same element | 🟡 Warning | Best Practice |
| VUE-003 | Unused component imports | 🔵 Info | Best Practice |
| VUE-004 | Missing prop validation | 🔵 Info | Best Practice |
| VUE-005 | Direct mutation of props | 🔴 Error | Correctness |
| VUE-006 | Using $refs excessively | 🟡 Warning | Best Practice |
| VUE-007 | Missing error handling in async methods | 🟡 Warning | Correctness |
| VUE-008 | Console statements | 🔵 Info | Best Practice |
| VUE-009 | Deep watchers without necessity | 🔵 Info | Performance |
| VUE-010 | Missing key for component transitions | 🟡 Warning | Correctness |

### 🧡 Svelte Rules (8)

| Rule ID | Name | Severity | Category |
|---------|------|----------|----------|
| SVELTE-001 | Missing key in {#each} | 🔴 Error | Correctness |
| SVELTE-002 | Unused variables | 🔵 Info | Best Practice |
| SVELTE-003 | Missing $ prefix for reactive stores | 🟡 Warning | Correctness |
| SVELTE-004 | Console statements | 🔵 Info | Best Practice |
| SVELTE-005 | Unnecessary reactive declarations | 🔵 Info | Best Practice |
| SVELTE-006 | Missing type annotations | 🔵 Info | Best Practice |
| SVELTE-007 | Accessibility issues (missing aria labels) | 🟡 Warning | Accessibility |
| SVELTE-008 | Large component files | 🟡 Warning | Best Practice |

### 🔴 Angular Rules (8)

| Rule ID | Name | Severity | Category |
|---------|------|----------|----------|
| ANGULAR-001 | Missing trackBy in *ngFor | 🟡 Warning | Performance |
| ANGULAR-002 | Using 'any' type | 🟡 Warning | Correctness |
| ANGULAR-003 | Console statements | 🔵 Info | Best Practice |
| ANGULAR-004 | Unused imports | 🔵 Info | Best Practice |
| ANGULAR-005 | Missing OnPush change detection | 🔵 Info | Performance |
| ANGULAR-006 | Direct DOM access | 🟡 Warning | Best Practice |
| ANGULAR-007 | Missing subscription unsubscribe | 🟡 Warning | Correctness |
| ANGULAR-008 | Large component files | 🟡 Warning | Best Practice |

### 📋 General Rules (15)

| Rule ID | Name | Severity | Category |
|---------|------|----------|----------|
| GEN-001 | File too long | 🟡 Warning | Best Practice |
| GEN-002 | Function too complex | 🟡 Warning | Best Practice |
| GEN-003 | Missing file header comments | 🔵 Info | Best Practice |
| GEN-004 | Inconsistent naming conventions | 🔵 Info | Best Practice |
| GEN-005 | TODO/FIXME/HACK comments | 🔵 Info | Best Practice |
| GEN-006 | Dead code (unused exports) | 🔵 Info | Best Practice |
| GEN-007 | Duplicate code blocks | 🟡 Warning | Best Practice |
| GEN-008 | Missing error handling | 🟡 Warning | Correctness |
| GEN-009 | Hardcoded strings | 🔵 Info | Best Practice |
| GEN-010 | Missing or inadequate comments | 🔵 Info | Best Practice |
| GEN-011 | Deep nesting | 🟡 Warning | Best Practice |
| GEN-012 | Magic numbers | 🔵 Info | Best Practice |
| GEN-013 | Large parameter lists | 🟡 Warning | Best Practice |
| GEN-014 | Missing return type annotations | 🔵 Info | Best Practice |
| GEN-015 | Inconsistent file naming | 🔵 Info | Best Practice |

### 🔒 Security Rules (10)

| Rule ID | Name | Severity | Category |
|---------|------|----------|----------|
| SEC-001 | eval() usage | 🔴 Error | Security |
| SEC-002 | innerHTML assignment | 🔴 Error | Security |
| SEC-003 | Hardcoded secrets/API keys | 🔴 Error | Security |
| SEC-004 | Using http:// instead of https:// | 🟡 Warning | Security |
| SEC-005 | SQL injection patterns | 🔴 Error | Security |
| SEC-006 | Path traversal patterns | 🔴 Error | Security |
| SEC-007 | Command injection patterns | 🔴 Error | Security |
| SEC-008 | Insecure random usage | 🟡 Warning | Security |
| SEC-009 | CORS wildcard configuration | 🟡 Warning | Security |
| SEC-010 | Sensitive data in localStorage | 🟡 Warning | Security |

### ⚡ Performance Rules (10)

| Rule ID | Name | Severity | Category |
|---------|------|----------|----------|
| PERF-001 | Large bundle imports | 🟡 Warning | Performance |
| PERF-002 | Missing lazy loading for routes | 🔵 Info | Performance |
| PERF-003 | Unoptimized images (no width/height) | 🔵 Info | Performance |
| PERF-004 | Synchronous file operations | 🟡 Warning | Performance |
| PERF-005 | Unnecessary re-renders patterns | 🔵 Info | Performance |
| PERF-006 | Missing debounce/throttle on events | 🔵 Info | Performance |
| PERF-007 | Large state objects | 🟡 Warning | Performance |
| PERF-008 | Unoptimized loops (nested forEach/map) | 🟡 Warning | Performance |
| PERF-009 | Memory leak patterns (event listeners not cleaned) | 🟡 Warning | Performance |
| PERF-010 | Missing virtualization for large lists | 🔵 Info | Performance |

---

## 💡 Design Philosophy & Roadmap

### 🎨 Design Philosophy

FrameScore is built on these core principles:

1. **Zero Dependency Principle** — Only the Python standard library is used, ensuring simple installation, stable execution, and no version conflicts
2. **Convention over Configuration** — Works out of the box with automatic framework detection, no complex config files needed
3. **Progressive Feedback** — Three severity levels (Error / Warning / Info) help developers prioritize the most critical issues first
4. **Quantifiable Metrics** — Translates code quality into intuitive scores and grades for easy team communication and tracking
5. **Framework Equality** — Equal depth of analysis for React, Vue, Svelte, and Angular

### 🛠️ Technical Choices

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Implementation language | Python | Rich text processing capabilities, excellent cross-platform compatibility |
| Dependency management | Zero external dependencies | Lowers installation barrier, avoids version conflicts |
| Parallelism strategy | Multi-threading (concurrent.futures) | I/O-bound tasks are well-suited for multi-threading |
| Rule engine | Regex-based pattern matching | Lightweight and efficient, no complex AST parser dependencies |
| Output formats | JSON / Table / Markdown | Covers CI/CD integration, terminal viewing, and documentation archiving |

### 🗺️ Roadmap

#### v1.x — Stabilization & Enhancement
- [ ] Custom rule configuration file support (`.framescorerc`)
- [ ] Additional framework-specific rules
- [ ] Web Components framework support
- [ ] HTML/CSS analysis rules

#### v2.0 — Intelligence Upgrade
- [ ] AST-based deep code analysis
- [ ] AI-assisted fix suggestions
- [ ] Code smell detection
- [ ] IDE plugin integration

#### v3.0 — Platform
- [ ] Web-based visualization dashboard
- [ ] Team collaboration and code quality comparison
- [ ] Historical trend analysis and prediction
- [ ] GitHub App / GitLab CI integration

---

## 📦 Installation & Deployment

### 📥 Installation Methods

```bash
# Method 1: Install from PyPI (recommended)
pip install framescore

# Method 2: Install latest dev version from GitHub
pip install git+https://github.com/gitstq/FrameScore.git

# Method 3: Install from source
git clone https://github.com/gitstq/FrameScore.git
cd FrameScore
pip install .
```

### 🐍 Python Version Support

| Python Version | Status |
|----------------|--------|
| 3.12 | ✅ Supported |
| 3.11 | ✅ Supported |
| 3.10 | ✅ Supported |
| 3.9 | ✅ Supported |
| 3.8 | ✅ Supported |
| < 3.8 | ❌ Not supported |

### 🔄 CI/CD Integration

Use FrameScore in your CI/CD pipeline for automated code quality checks:

**GitHub Actions Example:**

```yaml
name: Code Health Check

on: [push, pull_request]

jobs:
  framescore:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install FrameScore
        run: pip install framescore
      - name: Run FrameScore
        run: framescore scan . --format json --output report.json --severity warning
      - name: Check Score
        run: |
          SCORE=$(python -c "import json; print(json.load(open('report.json'))['health']['overall_score'])")
          if (( $(echo "$SCORE < 70" | bc -l) )); then
            echo "Score $SCORE is below threshold 70"
            exit 1
          fi
```

**GitLab CI Example:**

```yaml
code_health:
  stage: test
  image: python:3.11
  script:
    - pip install framescore
    - framescore scan . --format json --output report.json --severity warning
  artifacts:
    paths:
      - report.json
```

---

## 🤝 Contributing

We welcome and appreciate every contributor! Here is the guide for participating:

### 📌 Contribution Workflow

1. **Fork** this repository to your GitHub account
2. **Clone** your forked repository locally
3. **Create a branch**: `git checkout -b feature/your-feature-name`
4. **Develop and test**: Write code and ensure all tests pass
5. **Commit**: `git commit -m "feat: add your feature description"`
6. **Push**: `git push origin feature/your-feature-name`
7. **Open a Pull Request**: Create a PR on GitHub and describe your changes

### 📝 Commit Convention

Please follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation update
- `style:` Code formatting
- `refactor:` Code refactoring
- `test:` Test-related changes
- `chore:` Build/toolchain changes

### 🐛 Submitting Issues

When submitting an issue, please include:

- **Description** — A clear description of the problem or suggestion
- **Steps to reproduce** — How to reproduce the issue (if it's a bug)
- **Expected behavior** — What you expect the correct behavior to be
- **Environment** — Python version, OS, framework version, etc.
- **Screenshots/logs** — Relevant screenshots or error logs if possible

### ✅ Code of Conduct

- Respect all contributors
- Accept constructive code review feedback
- Maintain consistent code style
- Write tests for new features
- Update relevant documentation

---

## 📄 License

FrameScore is released under the [MIT License](https://opensource.org/licenses/MIT).

```
MIT License

Copyright (c) 2024 FrameScore Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">
  Made with ❤️ by <strong>FrameScore Team</strong><br/>
  If you find FrameScore helpful, please give it a ⭐ Star!
</p>
