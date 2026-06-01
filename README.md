# Abstract-LeetCode-Plus

![V1.1 dark theme available/深色模式支持](pic/dark_theme.png)

[Getting Started /快速开始](#getting-started--快速开始)

ABSTRACT is an intelligent study and review tool designed specifically for mastering LeetCode questions. It helps users organize, summarize, and retain key problem-solving patterns efficiently. With structured note-taking, spaced repetition, and AI-powered insights, ABSTRACT makes coding interview preparation faster and more effective.

ABSTRACT 是一款专为刷 LeetCode 打造的智能学习与复习辅助工具。它能够高效帮助用户梳理、总结并固化核心解题模式。通过结构化的笔记沉淀、渐进式重复记忆算法以及大模型的深度洞察，ABSTRACT 让技术面试的准备过程变得更加高效和精准。

* Contributor: [Jonas Li](yunzhe-li.top) ｜ FreakLu

---

![](pic/main.gif)

![](pic/use1.gif)

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

v1.1 (Current Version)
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

v1.1 (当前版本)
[增强] 增加零配置免费默认 LLM 接口；自定义 API / 供应商切换调整为进阶配置。

[新功能] 解耦大模型客户端，支持通过环境变量动态切换多厂商模型（OpenAI / DeepSeek / 硅基流动 SiliconFlow）。

[修复] 优化 Markdown 表格解析正则，完美兼容中英文双语题解抓取与自适应归档。

[增强] 本地 Excel 题解支持自动查重，检测到同名题目时自动刷新“上次复习时间（Last Viewed）”而不重复追加。

v1.0 (2025年2月20日)
特性：输入任一题号，自动生成结构化的题目分析，包括考察模式、复杂度分析以及最优解的 Python 代码。

支持将题目分析表一键下载至本地以便离线复习。

演示视频：YouTube 链接

---

### v1.1 In progress

What to expect /  geplant (后续更新计划):

* **Dark Mode / 深色模式**
* **History Sidebar / 历史错题本**
* **UI Overhaul / 排版优化**
* **Local Code  / 本地代码管理**
