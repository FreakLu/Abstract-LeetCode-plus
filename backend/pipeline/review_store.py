import os
import sqlite3
import re
import json
from datetime import datetime
from typing import Optional, List, Dict
from pipeline.solution_table_exporter import parse_markdown_table_rows

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "review.db")

def get_connection():
    """连接复习数据库，并让查询结果支持按字段名读取。"""
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_review_db():
    """初始化用于保存复习记录的 review_items 表。"""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS review_items (
                problem_number TEXT PRIMARY KEY,
                problem_title TEXT NOT NULL,
                last_viewed TEXT,

                tags_json TEXT,
                pattern TEXT,
                solution_approach TEXT,
                use_cases_json TEXT,

                mastery_level INTEGER DEFAULT 0,
                mistake_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'new',
                notes TEXT DEFAULT '',
                code_path TEXT DEFAULT '',

                raw_table_row TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()

def row_to_dict(row: sqlite3.Row) -> Dict:
    """将数据库记录转换为适合 API 和日志展示的字典。"""
    item = dict(row)

    try:
        item["tags"] = json.loads(item.pop("tags_json") or "[]")
    except json.JSONDecodeError:
        item["tags"] = []

    try:
        item["use_cases"] = json.loads(item.pop("use_cases_json") or "[]")
    except json.JSONDecodeError:
        item["use_cases"] = []

    return item

def list_review_items() -> List[Dict]:
    """查询全部复习记录，并按最近更新时间倒序排列。"""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM review_items
            ORDER BY updated_at DESC
            """
        ).fetchall()
        return [row_to_dict(row) for row in rows]

def get_review_item(problem_number: str) -> Optional[Dict]:
    """根据 LeetCode 题号查询一条复习记录。"""
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM review_items
            WHERE problem_number = ?
            """,
            (str(problem_number),),
        ).fetchone()

        if not row:
            return None

        return row_to_dict(row)

def save_review_item(item: Dict) -> Dict:
    """新增或更新一条复习记录，并保留用户维护的学习状态。"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO review_items (
                problem_number,
                problem_title,
                last_viewed,
                tags_json,
                pattern,
                solution_approach,
                use_cases_json,
                raw_table_row,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(problem_number) DO UPDATE SET
                problem_title = excluded.problem_title,
                last_viewed = excluded.last_viewed,
                tags_json = excluded.tags_json,
                pattern = excluded.pattern,
                solution_approach = excluded.solution_approach,
                use_cases_json = excluded.use_cases_json,
                raw_table_row = excluded.raw_table_row,
                updated_at = excluded.updated_at
            """,
            (
                str(item["problem_number"]),
                item["problem_title"],
                item.get("last_viewed"),
                json.dumps(item.get("tags", []), ensure_ascii=False),
                item.get("pattern", ""),
                item.get("solution_approach", ""),
                json.dumps(item.get("use_cases", []), ensure_ascii=False),
                item.get("raw_table_row", ""),
                now,
                now,
            ),
        )
        conn.commit()

    return get_review_item(str(item["problem_number"]))

def update_mastery_level(problem_number: str, mastery_level: int) -> Optional[Dict]:
    """更新指定题目的熟练度，并返回更新后的复习记录。"""
    if mastery_level not in {1, 2, 3}:
        raise ValueError("mastery_level must be 1, 2, or 3")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_connection() as conn:
        result = conn.execute(
            """
            UPDATE review_items
            SET mastery_level = ?,
                updated_at = ?
            WHERE problem_number = ?
            """,
            (mastery_level, now, str(problem_number)),
        )
        conn.commit()

    if result.rowcount == 0:
        return None

    return get_review_item(str(problem_number))

def parse_tags(text: str) -> List[str]:
    """将标签文本拆分为标签列表。"""
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        text = text[1:-1].strip()
    return [tag.strip() for tag in text.split(",") if tag.strip()]

def parse_pattern_solution(text: str) -> Dict[str, str]:
    """从混合文本中拆分题目模式和解题思路。"""
    labels = r"(考察模式|题目模式|Problem Pattern|解题思路|Solution Approach)\s*[:：]"
    matches = list(re.finditer(labels, text, flags=re.IGNORECASE))
    sections = {}

    for index, match in enumerate(matches):
        label = match.group(1).lower()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[label] = text[start:end].strip()

    pattern = (
        sections.get("考察模式")
        or sections.get("题目模式")
        or sections.get("problem pattern")
        or ""
    )
    solution_approach = (
        sections.get("解题思路")
        or sections.get("solution approach")
        or ""
    )

    if not pattern and not solution_approach:
        return {"pattern": text.strip(), "solution_approach": ""}

    return {"pattern": pattern, "solution_approach": solution_approach}

def parse_use_cases(text: str) -> List[str]:
    """将带编号的适用场景文本拆分为列表。"""
    parts = re.split(r"(?:^|\n)\s*\d+\.\s*", text)
    return [part.strip() for part in parts if part.strip()]

def parse_review_item_from_table(table_text: str) -> Optional[Dict]:
    """将 Markdown 六列表格的第一条数据转换为结构化复习记录。"""
    rows = parse_markdown_table_rows(table_text)
    if not rows:
        return None

    row = rows[0]
    pattern_solution = parse_pattern_solution(row[4])

    return {
        "problem_number": str(int(row[0])),
        "problem_title": row[1],
        "last_viewed": row[2],
        "tags": parse_tags(row[3]),
        "pattern": pattern_solution["pattern"],
        "solution_approach": pattern_solution["solution_approach"],
        "use_cases": parse_use_cases(row[5]),
        "raw_table_row": "|".join(row),
    }
