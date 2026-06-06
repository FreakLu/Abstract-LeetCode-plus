# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
import os
import re
import asyncio
from typing import Optional

from dotenv import load_dotenv
from pipeline.llm_client import auto_check_and_update_in_background
from pipeline.review_store import init_review_db, list_review_items, get_review_item
from pipeline.llm_client import LeetCodeAgent, create_llm_client, resolve_llm_model, resolve_llm_provider
from pipeline.solution_table_exporter import extract_table, parse_table_to_xlsx

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
if os.path.exists(ENV_PATH):
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    print(f"[Debug] Loaded env from: {ENV_PATH}")
    print(f"[Debug] LLM_PROVIDER: {os.getenv('LLM_PROVIDER')}")
    print(f"[Debug] LLM_MODEL: {os.getenv('LLM_MODEL')}")
    print(f"[Debug] APP_LANGUAGE: {os.getenv('APP_LANGUAGE')}")
else:
    print("[Info] backend/.env not found. Using the free default LLM provider.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_review_db()
    auto_check_and_update_in_background()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# define the request model
class QuestionRequest(BaseModel):
    question: str
    language: Optional[str] = None

def sanitize_question(raw_input: str) -> str:
    """
    Sanitize the question input by removing trailing punctuation marks.
    """
    if not raw_input: 
        return ""
    # Remove trailing punctuation marks
    clean_input = re.sub(r'[:;,.?？。：\s]+$', '', raw_input.strip())
    print(f"[Debug] Sanitized input: '{clean_input}'")
    return clean_input

@app.post("/api/solve/")
async def solve_question_api(request: QuestionRequest):
    user_input = sanitize_question(request.question)
    
    provider = resolve_llm_provider()
    model_name = resolve_llm_model(provider)
    llm_client = create_llm_client(provider=provider)
    agent = LeetCodeAgent(client=llm_client, model=model_name, language=request.language)

    async def generate():
        full_response_buffer = []
        try:
            for chunk in agent.stream_solution(user_input):
                full_response_buffer.append(chunk)
                yield chunk 
                await asyncio.sleep(0) 
        except Exception as e:
            yield f"\n[Service Error]: {str(e)}"
            return
            
        complete_response = "".join(full_response_buffer)
        table_data = extract_table(complete_response)
        if table_data:
            parse_table_to_xlsx(table_data)

    return StreamingResponse(generate(), media_type="text/event-stream")

@app.get("/api/update_problems_dict/")
async def update_problems_dict():
    result = agent.update_problems_dict()

@app.get("/api/download/")
async def download_excel():
    file_path = "./data/leetcode_solutions.xlsx"
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename="leetcode_solutions.xlsx")
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/api/review/items")
async def get_review_items_api():
    return {"items": list_review_items()}


@app.get("/api/review/items/{problem_number}")
async def get_review_item_api(problem_number: str):
    item = get_review_item(problem_number)
    if not item:
        raise HTTPException(status_code=404, detail="Review item not found")
    return item
