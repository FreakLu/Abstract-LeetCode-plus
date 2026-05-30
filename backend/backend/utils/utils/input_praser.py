import re

def sanitize_question(raw_input: str) -> str:
    """
    清洗用户输入，提取核心意图，剔除干扰字符
    """
    if not raw_input:
        return ""
        
    # 1. 剔除末尾的无意义标点符号（如冒号、问号等）
    clean_input = re.sub(r'[:;,.?？。：\s]+$', '', raw_input.strip())
    
    # 2. 如果只有数字，或者以 Leetcode 开头加数字，标准化为 "Leetcode X"
    # 这样 "Leetcode 20:" 就会被洗成 "Leetcode 20"
    match = re.search(r'(?:leetcode\s*)?(\d+)', clean_input.lower())
    if match:
        problem_number = match.group(1)
        return f"Leetcode {problem_number}"
        
    return clean_input