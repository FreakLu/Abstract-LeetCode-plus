"""
Markdown table parser example.

Run from the backend folder:

    python pipeline/table_parser_demo.py

It shows how LLM markdown table text becomes:
1. normalized table rows for Excel/export compatibility
2. one structured review item dict for SQLite and future cards
"""

from pprint import pprint
import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from pipeline.review_store import parse_review_item_from_table
from pipeline.solution_table_exporter import parse_markdown_table_rows


SAMPLE_TABLE = """
| 题号 | 名称 | 上次复习 | 标签 | 题目模式与解答思路 | 适用场景与扩展 |
|----|------|------------|-----|--------------------------|--------------------|
| 30 | Substring with Concatenation of All Words | 2026-06-02 | {Sliding Window, Hash Map, String, Two Pointers, Hashing} | 考察模式: 通过固定长度单词的滑动窗口，利用哈希表记录单词出现次数，判断窗口内是否恰好包含所有给定单词。<br> 解题思路: 先把 words 统计成频率表；然后对字符串 s 按单词长度的偏移量（0~wordLen-1）进行滑动窗口扫描；在窗口内维护当前单词计数，若出现多余或缺失的单词则移动左指针，直到窗口合法；当窗口大小等于所有单词长度之和且计数匹配时，记录左指针位置。 | 1. 多词子串匹配：寻找字符串中所有由给定单词集合组成的子串。<br> 2. 词频匹配问题：在文本中查找满足特定词频分布的子串。<br> 3. 变形题目：如“找出所有包含给定单词且每个单词出现次数不超过给定次数的子串”。 |
"""


def print_section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def main():
    print_section("1. 原始 Markdown 表格")
    print(SAMPLE_TABLE.strip())

    print_section("2. parse_markdown_table_rows(...) 的结果：兼容 Excel 的六列表格行")
    rows = parse_markdown_table_rows(SAMPLE_TABLE)
    pprint(rows)

    print_section("3. parse_review_item_from_table(...) 的结果：复习卡片需要的结构化数据")
    item = parse_review_item_from_table(SAMPLE_TABLE)
    pprint(item)


if __name__ == "__main__":
    main()
