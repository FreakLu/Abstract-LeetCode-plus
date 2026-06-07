import json
import math
import os
from datetime import date, datetime
from typing import Dict, List

from pipeline.review_store import list_review_items


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
PLAN_PATH = os.path.join(DATA_DIR, "study_plan.json")
PROBLEM_SETS_PATH = os.path.join(DATA_DIR, "problem_sets.json")
ALL_PROBLEMS_PATH = os.path.join(DATA_DIR, "leetcode_problems.json")
ALLOWED_STRATEGIES = {"classic", "high_frequency", "all"}


def load_problem_sets() -> Dict:
    """读取内置学习策略题单。"""
    try:
        with open(PROBLEM_SETS_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError) as error:
        print(f"[Study Plan Error] 读取内置题单失败：{error}")
        return {}


def get_strategy_problem_numbers(strategy: str) -> List[str]:
    """返回指定学习策略包含的题号列表。"""
    if strategy not in ALLOWED_STRATEGIES:
        raise ValueError("strategy must be classic, high_frequency, or all")

    if strategy == "all":
        try:
            with open(ALL_PROBLEMS_PATH, "r", encoding="utf-8") as file:
                problems = json.load(file)
                return list(problems.keys()) if isinstance(problems, dict) else []
        except (OSError, json.JSONDecodeError) as error:
            print(f"[Study Plan Error] 读取全部题目失败：{error}")
            return []

    problem_sets = load_problem_sets()
    return [
        str(problem_number)
        for problem_number in problem_sets.get(strategy, {}).get("problems", [])
    ]


def load_study_plan() -> Dict:
    """读取用户学习计划，尚未设置时返回空字典。"""
    if not os.path.exists(PLAN_PATH):
        return {}

    try:
        with open(PLAN_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError) as error:
        print(f"[Study Plan Error] 读取学习计划失败：{error}")
        return {}


def save_study_plan(target_date: str, strategy: str) -> Dict:
    """保存用户目标日期和学习策略。"""
    if strategy not in ALLOWED_STRATEGIES:
        raise ValueError("strategy must be classic, high_frequency, or all")

    parsed_target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
    if parsed_target_date < date.today():
        raise ValueError("target_date cannot be earlier than today")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    existing_plan = load_study_plan()
    plan = {
        "target_date": target_date,
        "strategy": strategy,
        "created_at": existing_plan.get("created_at", now),
        "updated_at": now,
    }

    os.makedirs(DATA_DIR, exist_ok=True)
    temporary_path = f"{PLAN_PATH}.tmp"

    with open(temporary_path, "w", encoding="utf-8") as file:
        json.dump(plan, file, ensure_ascii=False, indent=2)
    os.replace(temporary_path, PLAN_PATH)

    return plan


def calculate_study_progress(plan: Dict = None) -> Dict:
    """根据题单、目标日期和已见题目计算学习进度。"""
    plan = plan or load_study_plan()
    if not plan:
        return {}

    strategy = plan["strategy"]
    target_date = datetime.strptime(plan["target_date"], "%Y-%m-%d").date()
    strategy_problem_number_list = get_strategy_problem_numbers(strategy)
    strategy_problem_numbers = set(strategy_problem_number_list)
    completed_problem_numbers = {
        str(item["problem_number"])
        for item in list_review_items()
    }
    remaining_problem_numbers = [
        problem_number
        for problem_number in strategy_problem_number_list
        if problem_number not in completed_problem_numbers
    ]
    completed_count = len(strategy_problem_numbers & completed_problem_numbers)
    total_count = len(strategy_problem_numbers)
    remaining_count = max(total_count - completed_count, 0)
    remaining_days = max((target_date - date.today()).days, 0)
    daily_target = (
        math.ceil(remaining_count / remaining_days)
        if remaining_days > 0
        else remaining_count
    )

    problem_sets = load_problem_sets()
    strategy_info = problem_sets.get(strategy, {})

    return {
        **plan,
        "strategy_name": strategy_info.get("name", strategy),
        "strategy_description": strategy_info.get("description", ""),
        "total_problems": total_count,
        "completed_problems": completed_count,
        "remaining_problems": remaining_count,
        "remaining_problem_numbers": remaining_problem_numbers,
        "remaining_days": remaining_days,
        "daily_target": daily_target,
    }
