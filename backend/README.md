# Backend

## 快速启动

默认会使用免费的 Pollinations OpenAI-compatible 接口，不需要先创建 `backend/.env`。

### 前置依赖

请先安装：

- Python 3.8+
- Git

检查环境：

```bash
python --version
pip --version
```

Windows 如果提示无法识别 `pip`，请先试：

```powershell
py -m pip --version
```

如果这个命令可用，后续都使用 `py -m pip`，不要直接使用 `pip`。

### Windows PowerShell

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
py -m uvicorn main:app --reload --port 8000
```

如果 PowerShell 阻止虚拟环境激活：

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

然后重新运行：

```powershell
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m uvicorn main:app --reload --port 8000
```

后端启动后应运行在：

```text
http://127.0.0.1:8000
```

## 常见问题

### Windows: `pip` 无法识别

截图中这种报错：

```text
pip : 无法将“pip”项识别为 cmdlet、函数、脚本文件或可运行程序的名称
```

通常表示 Python/pip 没有正确加入 PATH。先使用：

```powershell
py -m pip install -r requirements.txt
```

如果 `py` 也无法识别，请重新安装 Python，并勾选：

```text
Add python.exe to PATH
```

### `uvicorn` 无法识别

不要直接依赖全局 `uvicorn` 命令，推荐使用：

```powershell
py -m uvicorn main:app --reload --port 8000
```

macOS / Linux 使用：

```bash
python3 -m uvicorn main:app --reload --port 8000
```

### 端口错误

请使用：

```bash
--port 8000
```

端口号最大是 `65535`。

### 没有 `.env` 文件

可以正常启动。项目默认会使用免费的 LLM 接口。（免费接口速度较慢，需要耐心等待）//最后测试时间2026年6月1日

只有需要自定义模型供应商或私有 API 时，才需要创建 `backend/.env`。

## 高级：自定义 API

只有需要切换供应商、模型或私有网关时，才需要在 `backend/.env` 中配置：

```env
# backend/.env

APP_LANGUAGE=zh

# 可选：default/free/pollinations, openai, deepseek, siliconflow, custom
LLM_PROVIDER=pollinations
LLM_MODEL=openai
```

### 使用内置供应商

```env
LLM_PROVIDER=siliconflow
SILICONFLOW_API_KEY=sk-your-siliconflow-key
LLM_MODEL=Qwen/Qwen2.5-72B-Instruct
```

也可以使用：

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key
LLM_MODEL=gpt-4o
```

```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-your-deepseek-key
LLM_MODEL=deepseek-chat
```

### 使用任意 OpenAI-compatible 网关

```env
LLM_PROVIDER=custom
LLM_BASE_URL=https://your-api.example.com/v1
LLM_API_KEY=sk-your-custom-key
LLM_MODEL=your-model-name
```
