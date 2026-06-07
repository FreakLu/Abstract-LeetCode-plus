# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
import os
import re
import asyncio
import json
from typing import Optional

from dotenv import load_dotenv
from pipeline.llm_client import auto_check_and_update_in_background
from pipeline.llm_client import LeetCodeAgent, create_llm_client, resolve_llm_model, resolve_llm_provider
from pipeline.solution_table_exporter import extract_table, parse_table_to_xlsx
from pipeline.activity_store import get_activity, record_activity
from pipeline.study_plan_store import (
    calculate_study_progress,
    load_problem_sets,
    load_study_plan,
    save_study_plan,
)

from pipeline.review_store import (
    init_review_db,
    list_review_items,
    get_review_item,
    parse_review_item_from_table,
    save_review_item,
    update_mastery_level,
)

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

class MasteryUpdateRequest(BaseModel):
    mastery_level: int

class StudyPlanRequest(BaseModel):
    target_date: str
    strategy: str

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
        if not table_data:
            print("[Review Store] 未从 LLM 输出中找到有效表格。")
            return

        parse_table_to_xlsx(table_data)

        try:
            review_item = parse_review_item_from_table(table_data)

            if not review_item:
                print("[Review Store] 表格存在，但未解析出有效复习记录。")
                return

            saved_item = save_review_item(review_item)
            record_activity("solve")
            log_item = {
                key: value
                for key, value in saved_item.items()
                if key != "raw_table_row"
            }

            print("[Review Store] 已保存复习记录：")
            print(json.dumps(log_item, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"[Review Store Error] 保存复习记录失败：{e}")

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


@app.patch("/api/review/items/{problem_number}/mastery")
async def update_mastery_level_api(problem_number: str, request: MasteryUpdateRequest):
    try:
        item = update_mastery_level(problem_number, request.mastery_level)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    if not item:
        raise HTTPException(status_code=404, detail="Review item not found")

    print(
        f"[Review Store] Updated mastery level: "
        f"LeetCode {problem_number} -> {request.mastery_level}"
    )
    record_activity("review")
    return item


@app.get("/api/review/activity")
async def get_review_activity_api(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    return {
        "activity": get_activity(
            start_date=start_date,
            end_date=end_date,
        )
    }


@app.get("/api/study-plan/strategies")
async def get_study_plan_strategies_api():
    problem_sets = load_problem_sets()
    return {
        "strategies": [
            {
                "id": strategy_id,
                "name": strategy.get("name", strategy_id),
                "description": strategy.get("description", ""),
            }
            for strategy_id, strategy in problem_sets.items()
        ]
    }


@app.get("/api/study-plan")
async def get_study_plan_api():
    plan = load_study_plan()
    return {
        "plan": calculate_study_progress(plan) if plan else None
    }


@app.put("/api/study-plan")
async def save_study_plan_api(request: StudyPlanRequest):
    try:
        plan = save_study_plan(
            target_date=request.target_date,
            strategy=request.strategy,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {
        "plan": calculate_study_progress(plan)
    }
