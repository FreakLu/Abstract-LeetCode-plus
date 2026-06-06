import os
import sqlite3
import re
from datetime import datetime
from typing import Optional, List, Dict
from pipeline.solution_table_exporter import parse_markdown_table_rows

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "review.db")

def get_connection():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_review_db():
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
    return dict(row)

def list_review_items() -> List[Dict]:
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

def parse_tags(text: str) -> List[str]:
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        text = text[1:-1].strip()
    return [tag.strip() for tag in text.split(",") if tag.strip()]

def parse_pattern_solution(text: str) -> Dict[str, str]:
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
    parts = re.split(r"(?:^|\n)\s*\d+\.\s*", text)
    return [part.strip() for part in parts if part.strip()]

def parse_review_item_from_table(table_text: str) -> Optional[Dict]:
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
