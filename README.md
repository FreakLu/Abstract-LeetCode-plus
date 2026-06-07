# Abstract-LeetCode-Plus

![V1.1 dark theme available/深色模式支持](pic/main.png)

[Getting Started /快速开始](#getting-started--快速开始)

ABSTRACT is an intelligent study and review tool designed specifically for mastering LeetCode questions. It helps users organize, summarize, and retain key problem-solving patterns efficiently. With structured note-taking, spaced repetition, and AI-powered insights, ABSTRACT makes coding interview preparation faster and more effective.

ABSTRACT 是一款专为刷 LeetCode 打造的智能学习与复习辅助工具。它能够高效帮助用户梳理、总结并固化核心解题模式。通过结构化的笔记沉淀、渐进式重复记忆算法以及大模型的深度洞察，ABSTRACT 让技术面试的准备过程变得更加高效和精准。

* Contributor: [Jonas Li](yunzhe-li.top) ｜ FreakLu

---

---

### Getting Started / 快速开始

The backend ships with a free default LLM endpoint, so `.env` is optional for quick installs. For custom API providers, see [backend/README.md](backend/README.md).

后端默认使用免费的 LLM 接口，快速安装不需要先配置 `.env`。如需切换自定义 API 或供应商，请参考 [backend/README.md](backend/README.md)。

Before starting, install:

- Python 3.8+
- Node.js 18+
- Git

安装前请确认已经安装：

- Python 3.8+
- Node.js 18+
- Git

Check your environment / 检查环境：

```bash
python --version
pip --version
node --version
npm --version
```

On Windows, if `pip` is not recognized, use `py -m pip` instead.

Windows 如果提示无法识别 `pip`，请改用 `py -m pip`。

#### Backend / 后端

Windows PowerShell:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
py -m uvicorn main:app --reload --port 8000
```

macOS / Linux:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m uvicorn main:app --reload --port 8000
```

#### Frontend / 前端

Open another terminal / 打开另一个终端：

```bash
cd frontend
npm install
npm start
```

Then open / 然后打开：

```text
http://localhost:3000
```

Backend runs at / 后端运行在：

```text
http://127.0.0.1:8000
```

Common issues are listed in [backend/README.md](backend/README.md).

常见问题请看 [backend/README.md](backend/README.md)。

---

### Version History

v1.2 (Current Version)
[Feat] Introduced the redesigned Study Workspace, combining question input, structured answer view, review gallery, and learning overview.

[Feat] Added SQLite-backed review cards with sorting, tag filtering, pinyin-aware search suggestions, mastery updates, and expanded solution details.

[Feat] Added persistent study plans with Classic 150, High Frequency 100, and All Problems strategies, including remaining days, daily targets, and completion progress.

[Feat] Added next-problem recommendations with sequential and random selection from unfinished problems in the active study plan.

[Feat] Added JSON-based Solve / Review activity tracking with 42-cell monthly calendars and yearly activity views.

[Enhance] Improved Markdown table cleanup, SQLite storage, Excel exports, and the visual guidance of primary homepage actions.

v1.1
[Enhance] Added a zero-config free default LLM endpoint. Custom API providers are now an advanced configuration path.

[Feat] Added multi-provider support (OpenAI / DeepSeek / SiliconFlow) via environment variables.

[Fix] Relaxed regex parsing to fully support dual-language (English/Chinese) table extractions.

[Enhance] Implemented automatic duplicate checking and dynamic "Last Viewed" date updates in the Excel tracker.

v1.0 (Feb 20, 2025)
Features: Enter one question, abstracts generate the structured question analysis including the question patterns, complexity analysis, and code for the exact best solution.  

Download the question analysis sheet to local for further review.  

Demo Video: YouTube Link  

---

### Version History / 版本历史

v1.2（当前版本）
[新功能] 重构学习工作区，整合题目输入、结构化题解、复习陈列室和学习概览。

[新功能] 增加基于 SQLite 的复习卡片，支持排序、标签筛选、拼音搜索联想、熟练度更新和题解详情扩展。

[新功能] 增加常驻学习计划，支持经典 150、高频 100 和全部题目策略，并计算剩余天数、每日目标与完成进度。

[新功能] 增加下一题推荐，可从当前计划的未完成题目中按顺序或随机选择。

[新功能] 增加基于 JSON 的 Solve / Review 学习活跃度记录，支持补齐 42 个日期格的月视图和年视图。

[增强] 优化 Markdown 表格清洗、SQLite 入库、Excel 导出，以及主页主要操作入口的视觉引导。

v1.1
[增强] 增加零配置免费默认 LLM 接口；自定义 API / 供应商切换调整为进阶配置。

[新功能] 解耦大模型客户端，支持通过环境变量动态切换多厂商模型（OpenAI / DeepSeek / 硅基流动 SiliconFlow）。

[修复] 优化 Markdown 表格解析正则，完美兼容中英文双语题解抓取与自适应归档。

[增强] 本地 Excel 题解支持自动查重，检测到同名题目时自动刷新“上次复习时间（Last Viewed）”而不重复追加。

v1.0 (2025年2月20日)
特性：输入任一题号，自动生成结构化的题目分析，包括考察模式、复杂度分析以及最优解的 Python 代码。

支持将题目分析表一键下载至本地以便离线复习。

演示视频：YouTube 链接

---

### Roadmap / 后续更新计划

What to expect / 后续更新计划：

* **End-to-end integration and build verification / 完整前后端联调与构建验证**
* **Local Code Management / 本地代码管理**
* **More Study Plan Strategies / 更多学习计划策略**
