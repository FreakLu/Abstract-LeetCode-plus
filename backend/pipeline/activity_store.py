import json
import os
from datetime import date
from typing import Dict, Optional


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
ACTIVITY_PATH = os.path.join(DATA_DIR, "review_activity.json")
ALLOWED_ACTIVITY_TYPES = {"solve", "review"}


def load_activity() -> Dict:
    """读取全部学习活跃度数据，文件不存在或损坏时返回空字典。"""
    if not os.path.exists(ACTIVITY_PATH):
        return {}

    try:
        with open(ACTIVITY_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError) as error:
        print(f"[Activity Store Error] 读取活跃度数据失败：{error}")
        return {}


def record_activity(activity_type: str) -> None:
    """为今天增加一次题解生成或复习确认活动。"""
    if activity_type not in ALLOWED_ACTIVITY_TYPES:
        raise ValueError("activity_type must be 'solve' or 'review'")

    activity = load_activity()
    today = date.today().isoformat()
    today_activity = activity.setdefault(today, {"solve": 0, "review": 0})
    today_activity[activity_type] = int(today_activity.get(activity_type, 0)) + 1

    os.makedirs(DATA_DIR, exist_ok=True)
    temporary_path = f"{ACTIVITY_PATH}.tmp"

    try:
        with open(temporary_path, "w", encoding="utf-8") as file:
            json.dump(activity, file, ensure_ascii=False, indent=2, sort_keys=True)
        os.replace(temporary_path, ACTIVITY_PATH)
    except OSError as error:
        print(f"[Activity Store Error] 写入活跃度数据失败：{error}")
        if os.path.exists(temporary_path):
            os.remove(temporary_path)


def get_activity(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict:
    """返回指定日期范围内的活跃度，并为每天补充总次数。"""
    activity = load_activity()
    result = {}

    for activity_date, counts in activity.items():
        if start_date and activity_date < start_date:
            continue
        if end_date and activity_date > end_date:
            continue

        solve_count = int(counts.get("solve", 0))
        review_count = int(counts.get("review", 0))
        result[activity_date] = {
            "solve": solve_count,
            "review": review_count,
            "total": solve_count + review_count,
        }

    return result
