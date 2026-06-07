"""
review_store.py 的 SQLite 操作示例。

包含几个基础动作：

1. 创建表
2. 查看表结构
3. 插入数据
4. 查询数据
5. 更新数据
6. 按条件筛选数据

运行方式：

    python pipeline/review_store_demo.py

这个脚本使用内存数据库，不会创建或修改 backend/data/review.db。
"""

import sqlite3
import json
from datetime import datetime
from pprint import pprint


CREATE_TABLE_SQL = """
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


def row_to_dict(row):
    """
    sqlite3.Row 不是普通 dict，但它可以通过字段名读取值。
    FastAPI 返回 JSON 时，普通 dict 更方便，所以这里统一转换一下。
    """
    return dict(row)


def print_section(title):
    """
    只是为了让终端输出更好读，和 SQLite 本身没有关系。
    """
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def main():
    # ":memory:" 表示这个数据库只存在于本次脚本运行期间，脚本结束后自动消失。
    # 如果换成 sqlite3.connect("review.db")，才会真的生成一个数据库文件。
    conn = sqlite3.connect(":memory:")

    # 设置后，查询结果可以像字典一样通过 row["字段名"] 读取。
    # 不设置的话，查询结果会更像 tuple，例如 ("20", "Valid Parentheses")。
    conn.row_factory = sqlite3.Row

    print_section("1. 创建 review_items 表")
    print(CREATE_TABLE_SQL.strip())

    # execute(...) 执行一段 SQL。
    # 这里的 SQL 是 CREATE TABLE，也就是创建一张表。
    # IF NOT EXISTS 表示：如果表已经存在，就不要重复创建，也不要报错。
    conn.execute(CREATE_TABLE_SQL)

    # commit() 表示确认这次改动。
    # 对 CREATE / INSERT / UPDATE / DELETE 这类会修改数据库的操作，通常都要 commit。
    conn.commit()

    print_section("2. 查看表结构：PRAGMA table_info(review_items)")

    # PRAGMA table_info(...) 不是查询业务数据，而是在问 SQLite：
    # “请告诉我 review_items 这张表有哪些列，每列是什么类型。”
    #
    # 它返回的 cid/name/type/notnull/default/pk 是 SQLite 自动给出的表结构说明：
    # - cid: column id，也就是“这一列在表里的顺序编号”，从 0 开始。
    #   它不是我们业务里的题目 id，也不是数据库主键。
    # - name: 列名，例如 problem_number。
    # - type: 列类型，例如 TEXT / INTEGER。
    # - notnull: 是否不允许为空。1 表示 NOT NULL，0 表示可以为空。
    # - dflt_value: 默认值。
    # - pk: 是否是主键。1 表示主键，0 表示不是。
    table_info = conn.execute("PRAGMA table_info(review_items)").fetchall()
    for column in table_info:
        print(
            {
                "列序号(cid，不是业务字段)": column["cid"],
                "列名": column["name"],
                "类型": column["type"],
                "是否非空": column["notnull"],
                "默认值": column["dflt_value"],
                "是否主键": column["pk"],
            }
        )

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print_section("3. 插入两条复习记录")

    # INSERT INTO 表名 (...) VALUES (...) 表示插入一行数据。
    # 问号 ? 是占位符，真正的值放在后面的 tuple 里。
    # 这样写比字符串拼接安全，也能避免引号、特殊字符带来的问题。
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
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "20",
            "Valid Parentheses",
            "2026-06-01",
            json.dumps(["Stack", "String"]),
            "Stack matching",
            "Use a stack to match opening and closing brackets.",
            json.dumps(["Use when the problem needs last-in-first-out matching."]),
            now,
            now,
        ),
    )

    # 第二条记录演示：有些字段可以不使用默认值，而是手动指定。
    # 例如 mastery_level=1、mistake_count=3、status="weak"。
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
            mastery_level,
            mistake_count,
            status,
            notes,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "30",
            "Substring with Concatenation of All Words",
            "2026-06-01",
            json.dumps(["Hash Table", "Sliding Window"]),
            "Sliding window by word length",
            "Use sliding windows grouped by word length.",
            json.dumps(["Use when matching fixed-length chunks repeatedly."]),
            1,
            3,
            "weak",
            "Need to review window reset logic.",
            now,
            now,
        ),
    )
    conn.commit()
    print("已插入 LeetCode 20 和 LeetCode 30。")

    print_section("4. 查询全部记录，按更新时间从新到旧排序")

    # SELECT * 表示查询所有列。
    # FROM review_items 表示从 review_items 这张表里查。
    # ORDER BY updated_at DESC 表示按 updated_at 倒序排列，也就是最新的在前。
    # fetchall() 表示取回所有查询结果。
    rows = conn.execute(
        """
        SELECT *
        FROM review_items
        ORDER BY updated_at DESC
        """
    ).fetchall()
    pprint([row_to_dict(row) for row in rows])

    print_section("5. 按 problem_number 查询单条记录")

    # WHERE problem_number = ? 表示只查询题号等于指定值的那一行。
    # fetchone() 表示只取一条结果。
    # 如果没有查到，fetchone() 会返回 None。
    row = conn.execute(
        """
        SELECT *
        FROM review_items
        WHERE problem_number = ?
        """,
        ("30",),
    ).fetchone()
    pprint(row_to_dict(row))

    print_section("6. 更新某一题的错误次数和状态")

    # UPDATE 表名 SET ... WHERE ... 表示更新已有数据。
    # mistake_count = mistake_count + 1 表示在原来的错误次数基础上加 1。
    # WHERE problem_number = ? 很重要：没有 WHERE 会把整张表都更新掉。
    conn.execute(
        """
        UPDATE review_items
        SET mistake_count = mistake_count + 1,
            status = ?,
            updated_at = ?
        WHERE problem_number = ?
        """,
        ("weak", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "20"),
    )
    conn.commit()

    # 更新完之后，再查一次第 20 题。
    # 这里没有 SELECT *，而是只查我们关心的几列。
    row = conn.execute(
        """
        SELECT problem_number, problem_title, mistake_count, status, updated_at
        FROM review_items
        WHERE problem_number = ?
        """,
        ("20",),
    ).fetchone()
    pprint(row_to_dict(row))

    print_section("7. 只查询状态为 weak 的题目")

    # 这个查询演示“筛选”：
    # WHERE status = ? 只取状态为 weak 的题目。
    # ORDER BY mistake_count DESC 让错误次数最多的排在前面。
    rows = conn.execute(
        """
        SELECT problem_number, problem_title, mistake_count, status
        FROM review_items
        WHERE status = ?
        ORDER BY mistake_count DESC
        """,
        ("weak",),
    ).fetchall()
    pprint([row_to_dict(row) for row in rows])

    print_section("8. 重复写入第 20 题，并保留用户学习状态")

    # 这里使用与 save_review_item(...) 相同的写入逻辑：
    # 题号不存在时插入；题号已存在时，只更新题解内容，不覆盖错误次数、状态和笔记。
    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
            "20",
            "Valid Parentheses",
            "2026-06-06",
            json.dumps(["Stack", "String", "Simulation"]),
            "Stack matching with bracket pairs",
            "Use a mapping table and stack to validate each closing bracket.",
            json.dumps(["Bracket matching", "Nested structure validation"]),
            "|20|Valid Parentheses|updated row|",
            updated_at,
            updated_at,
        ),
    )
    conn.commit()

    row = conn.execute(
        """
        SELECT
            problem_number,
            last_viewed,
            tags_json,
            pattern,
            mistake_count,
            status,
            notes,
            updated_at
        FROM review_items
        WHERE problem_number = ?
        """,
        ("20",),
    ).fetchone()
    pprint(row_to_dict(row))

    # 关闭连接。内存数据库会在这里消失。
    conn.close()


if __name__ == "__main__":
    main()
