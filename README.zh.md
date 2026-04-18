# CC+Obsidian — 个人知识摄取系统

> **Claude Code + Obsidian + DeepSeek** · 将任意网页或 PDF 转化为结构化个人知识库

[English Documentation](README.md)

---

## 这是什么

一套个人知识管理工作流，将网页内容和 PDF 转化为结构化的 Obsidian 笔记，并配以可视化 Canvas 知识矩阵和数据库视图，整个过程由 AI 驱动。

**不是发布工具。** 这是一个私人知识积累引擎。

```
网页 URL / PDF
    ↓  抓取（defuddle CLI）
_raw_sources/           ← 不可变的原始内容存档
    ↓  提取（DeepSeek API）
[topic]/                ← 带 frontmatter 的结构化 .md 笔记
    ↓  放置（用户决定位置）
[topic].canvas          ← 可视化知识矩阵
[topic].base            ← 数据库视图（Obsidian Bases 插件）
```

**编排大脑：** Claude Code（或任何兼容 Claude 的 Agent）
**知识提取：** 仅 DeepSeek API — Claude 负责其余所有步骤

---

## 目录结构

```
CC+Obsidian/
├── .claude/
│   ├── commands/
│   │   └── knowledge-intake.md     ← /knowledge-intake 斜杠命令
│   └── skills/
│       ├── knowledge-intake.md     ← 5步工作流 Skill
│       ├── defuddle/               ← 网页抓取 Skill（kepano）
│       ├── json-canvas/            ← Canvas 操作 Skill（kepano）
│       ├── obsidian-bases/         ← Bases 插件 Skill（kepano）
│       ├── obsidian-cli/           ← Obsidian CLI Skill（kepano）
│       └── obsidian-markdown/      ← Markdown 格式化 Skill（kepano）
├── config/
│   ├── extraction_prompts.json     ← DeepSeek 提示词模板
│   └── topics.json                 ← 已注册的 Topic 列表
├── scripts/
│   └── intake.py                   ← 可移植 Python 脚本（DeepSeek + 抓取）
├── skills/                         ← 通用 Skills（多 Agent 兼容）
├── skills-lock.json                ← Skill 版本锁定文件
├── CLAUDE.md                       ← Vault 上下文（Claude 每次自动加载）
├── [topic].canvas                  ← 每个 Topic 的可视化知识矩阵
└── [topic].base                    ← 每个 Topic 的数据库视图
```

---

## 前置条件

| 需求 | 说明 |
|------|------|
| [Claude Code](https://claude.ai/code) | CLI 版或 VS Code 插件 |
| [Obsidian](https://obsidian.md) | 桌面客户端 |
| Obsidian **Canvas** 插件 | 内置核心插件，在设置中启用 |
| Obsidian **Bases** 插件 | 社区插件，从插件市场安装 |
| Python 3.10+ | 运行 `scripts/intake.py` |
| Node.js 18+ | 运行 `defuddle` CLI 和 `npx skills` |
| DeepSeek API Key | [platform.deepseek.com](https://platform.deepseek.com) 申请 |

---

## 快速开始

### 1. 克隆并打开

```bash
git clone https://github.com/Xin-MediaGeek/CC-Obsidian.git
cd CC-Obsidian
```

将该文件夹同时作为 **Obsidian Vault** 和 **Claude Code 项目**打开。

### 2. 安装 Python 依赖

```bash
pip install openai requests
```

### 3. 安装 defuddle CLI

```bash
npm install -g defuddle
```

### 4. 安装 Obsidian Skills（推荐但非必须）

```bash
npx skills add git@github.com:kepano/obsidian-skills.git
```

选择全部 5 个 Skill → 安装范围选 **Project** → Agent 选 **Claude Code**

### 5. 设置 DeepSeek API Key

**Windows：**
```powershell
setx DEEPSEEK_API_KEY "你的Key"
```

**macOS/Linux：**
```bash
export DEEPSEEK_API_KEY="你的Key"
# 添加到 ~/.zshrc 或 ~/.bashrc 使其永久生效
```

### 6. 开始第一次知识摄取

在 Claude Code 中打开此目录，输入：

```
/knowledge-intake
```

按提示提供 URL 或 PDF 路径。

---

## 5步知识摄取工作流

| 步骤 | 发生了什么 | 执行者 |
|------|-----------|--------|
| **1. 摄取** | 抓取网页或读取 PDF → 保存原始内容到 `_raw_sources/` | Claude + defuddle CLI |
| **2. 去重** | 检查是否存在重复或相关的已有笔记 | Claude |
| **3. 提取** | 确认提示词 → 调用 DeepSeek API → 生成 `.md` 笔记 | DeepSeek API |
| **4. Canvas 放置** | 询问每个笔记放在哪里 → 更新 `.canvas` JSON | Claude（你来决定） |
| **5. 完成** | 打印摘要，提示是否打开 `.base` 视图 | Claude |

---

## 笔记 Frontmatter 结构

每条处理后的笔记包含：

```yaml
---
title: "概念标题"
date: 2026-04-18
source_url: "https://..."
source_raw: "_raw_sources/20260418_domain_slug.md"
topic: ai-engineering
tags: [ai-engineering, llm]
summary: "一句话摘要"
status: draft   # draft | reviewed
---
```

---

## 提取提示词模板

`config/extraction_prompts.json` 内置三个模板：

| 模板 | 适用场景 |
|------|---------|
| `default` | 通用文章、博客帖子 |
| `technical-deep-dive` | 技术文档、架构设计、代码密集型内容 |
| `concept-map` | 概念关联性强的内容 |

每次提取前会展示上次使用的提示词，你可以确认、修改或切换模板。

---

## 新增 Topic

摄取新内容时，如果不属于已注册的 Topic，Claude 会询问：

1. 添加到已有 Topic
2. 新建 Topic（自动创建文件夹 + `.canvas` + `.base`）
3. 暂存到 `_staging/` 等待后续分类

---

## Canvas 节点格式

`.canvas` JSON 中每个节点显示：

```
**概念标题**
_一句话摘要_

[[笔记文件名]]
```

分组（Group）代表子主题，连接线（Edge）代表带标签的关系。最多 2 层结构：Topic（Canvas 文件）→ 子主题（Canvas 内分组）。

---

## intake.py CLI 参考

跨环境使用（无需 Claude）：

```bash
# 仅抓取 URL 并保存原始内容
python scripts/intake.py --url URL --slug my-slug --raw-only

# 从已有原始文件提取笔记
python scripts/intake.py --extract --source _raw_sources/file.md --topic my-topic

# 完整流程：抓取 + 提取
python scripts/intake.py --url URL --topic my-topic

# 使用自定义提示词
python scripts/intake.py --extract --source file.md --prompt "你的提示词"

# 使用 deepseek-reasoner 模型（复杂主题）
python scripts/intake.py --extract --source file.md --model deepseek-reasoner
```

---

## 致谢

- [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) — 面向 Claude Code 的 Obsidian Skill 文件
- [defuddle](https://github.com/kepano/defuddle) — 干净的网页内容提取
- [DeepSeek](https://deepseek.com) — 知识提取 API
- 灵感来源：*Claude Code + Obsidian，打造个人一站式内容创作管理引擎*

---

## License

MIT
