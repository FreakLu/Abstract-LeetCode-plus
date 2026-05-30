# Backend

## API 配置

在backend根目录下 配置如下.env文件(需要自建)

```env
# backend/.env

APP_LANGUAGE=zh
# API Provider: openai, deepseek, siliconflow
LLM_PROVIDER=siliconflow

# API Keys
OPENAI_API_KEY=sk-your-openai-key
DEEPSEEK_API_KEY=sk-your-deepseek-key
SILICONFLOW_API_KEY=sk-your-siliconflow-key

# Model
LLM_MODEL=Qwen/Qwen2.5-72B-Instruct
```

构建后端虚拟环境

```bash
conda create -n leetcode_env python=3.8.20
conda activate leetcode_env
pip install -r requirements.txt
```

启动后端服务

```bash
uvicorn main:app --reload --port 8000
```
