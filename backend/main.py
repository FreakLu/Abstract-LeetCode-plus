# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import re
import asyncio

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, '.env') 
if os.path.exists(ENV_PATH):
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    print(f"[Debug] Loaded from: {ENV_PATH}")
    print(f"[Debug] LANGUAGE value: {os.getenv('APP_LANGUAGE')}")
else:
    print(f"[Error] .env file not found at: {ENV_PATH}")

# 从你现有的 pipeline 中导入你的核心业务代码！
from pipeline.llm_client import LeetCodeAgent, create_llm_client
from pipeline.parse_response_to_csv import extract_table, parse_table_to_xlsx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. 定义前端传过来的数据结构
class QuestionRequest(BaseModel):
    question: str

def sanitize_question(raw_input: str) -> str:
    """
    只剥离末尾的标点符号，绝对不截断正文
    """
    if not raw_input: 
        return ""
    # 仅替换结尾的冒号、问号等，保留用户输入的原始全貌
    clean_input = re.sub(r'[:;,.?？。：\s]+$', '', raw_input.strip())
    print(f"👉 [Debug] 传给后端的真实输入: '{clean_input}'") # 加上这句用于排错
    return clean_input

# 3. 核心 API：流式对话
@app.post("/api/solve/")
async def solve_question_api(request: QuestionRequest):
    user_input = sanitize_question(request.question)
    
    # 初始化你的 Agent (复用你原有的逻辑)
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    model_name = os.getenv("LLM_MODEL", "gpt-4o")
    llm_client = create_llm_client(provider=provider)
    agent = LeetCodeAgent(client=llm_client, model=model_name, language=None)

    async def generate():
        full_response_buffer = []
        try:
            # 注意：这里需要你确保 agent 内部有 yield 流式输出的逻辑
            for chunk in agent.stream_solution(user_input):
                full_response_buffer.append(chunk)
                yield chunk 
                await asyncio.sleep(0) 
        except Exception as e:
            yield f"\n[Service Error]: {str(e)}"
            return
            
        # 等前端字符全部跳完后，后台静默生成 Excel
        complete_response = "".join(full_response_buffer)
        table_data = extract_table(complete_response)
        if table_data:
            parse_table_to_xlsx(table_data)

    return StreamingResponse(generate(), media_type="text/event-stream")

# 4. 下载接口平替
@app.get("/api/download/")
async def download_excel():
    file_path = "./data/leetcode_solutions.xlsx"
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename="leetcode_solutions.xlsx")
    raise HTTPException(status_code=404, detail="File not found")