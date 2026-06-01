from openai import OpenAI
from openai import OpenAIError
import os
import time
import re
from typing import List, Dict, Optional
import json
import requests
import threading

DEFAULT_LLM_PROVIDER = "pollinations"

DEFAULT_MODELS = {
    "pollinations": "openai",
    "openai": "gpt-4o",
    "deepseek": "deepseek-chat",
    "siliconflow": "Qwen/Qwen2.5-72B-Instruct",
    "custom": "gpt-4o-mini",
}

PROVIDER_ALIASES = {
    "default": "pollinations",
    "free": "pollinations",
    "openai-compatible": "custom",
}


_PROBLEM_DICT_CACHE = None
def get_or_load_problem_dict() -> dict:
        global _PROBLEM_DICT_CACHE
        if _PROBLEM_DICT_CACHE is not None:
            return _PROBLEM_DICT_CACHE

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(project_root, "data", "leetcode_problems.json")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                _PROBLEM_DICT_CACHE = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            _PROBLEM_DICT_CACHE = {}
        return _PROBLEM_DICT_CACHE
def update_problem_dict_from_web():
    """
    Updates the problem dictionary from the web.

    Returns:
        None
    """
    # Fetch the latest problem list from theetCode API
    url = "https://leetcode.com/graphql"

    payload = {
        "query": """
        query {
            allQuestions {
                questionFrontendId
                title
            }
        }
        """
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        questions = response.json().get("data", {}).get("allQuestions", [])
        
        new_dict = {}
        for q in questions:
            if q.get("questionFrontendId") and q.get("title"):
                new_dict[str(q.get("questionFrontendId"))] = q.get("title")
                
        if not new_dict:
            return

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(project_root, "data", "leetcode_problems.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(new_dict, f, indent=4, ensure_ascii=False)
            
        global _PROBLEM_DICT_CACHE
        _PROBLEM_DICT_CACHE = new_dict
        print(f"\n[Info] sync problem dict from web, total {len(new_dict)} problems.")
    except Exception as e:
        print(f"\n[Error] sync problem dict from web failed ({e})")


def should_update_dict() -> bool:
    """
    Check if the problem dictionary should be updated.

    Returns:
        bool: True if the dictionary should be updated, False otherwise.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(project_root,"data","leetcode_problems.json")
    
    if not os.path.exists(file_path):
        return True
        
    last_modified_time = os.path.getmtime(file_path)
    current_time = time.time()
    
    return (current_time - last_modified_time) > 604800 # 7 days

def auto_check_and_update_in_background():
    """
    主程序调用的入口：负责判断，并决定是否要“外包”给子线程。
    """
    if should_update_dict():
        print("[Info] detect problem dict is stale, start to update from web...")
        updater_thread = threading.Thread(target=update_problem_dict_from_web, daemon=True)
        updater_thread.start()
    else:
        print("[Info] problem dict is fresh, no need to update.")


def resolve_llm_provider(provider: Optional[str] = None) -> str:
    """
    Returns the configured provider. The default path is intentionally free and
    zero-config so quick installs do not need an API key before trying the app.
    """
    configured_provider = provider or os.getenv("LLM_PROVIDER") or DEFAULT_LLM_PROVIDER
    configured_provider = configured_provider.strip().lower()
    return PROVIDER_ALIASES.get(configured_provider, configured_provider)


def resolve_llm_model(provider: Optional[str] = None) -> str:
    provider = resolve_llm_provider(provider)
    return os.getenv("LLM_MODEL") or DEFAULT_MODELS.get(provider, DEFAULT_MODELS["pollinations"])


def _required_env(name: str, provider: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    raise ValueError(f"Provider '{provider}' requires {name}. Use the default provider for zero-config setup.")


def create_llm_client(provider: Optional[str] = None) -> OpenAI:
    """
    Creates and returns an OpenAI-compatible client based on the specified provider.
    
    Args:
        provider (str): The API provider ("pollinations", "openai", "deepseek",
            "siliconflow", or "custom").
        
    Returns:
        OpenAI: The initialized client.
    """
    provider = resolve_llm_provider(provider)

    if provider == "pollinations":
        return OpenAI(
            api_key=os.getenv("POLLINATIONS_API_KEY") or os.getenv("LLM_API_KEY") or "anonymous",
            base_url=os.getenv("POLLINATIONS_BASE_URL") or "https://text.pollinations.ai/openai"
        )
    
    elif provider == "openai":
        return OpenAI(api_key=_required_env("OPENAI_API_KEY", provider))
        
    elif provider == "deepseek":
        return OpenAI(
            api_key=_required_env("DEEPSEEK_API_KEY", provider),
            base_url=os.getenv("DEEPSEEK_BASE_URL") or "https://api.deepseek.com"
        )
        
    elif provider == "siliconflow":
        return OpenAI(
            api_key=_required_env("SILICONFLOW_API_KEY", provider),
            base_url=os.getenv("SILICONFLOW_BASE_URL") or "https://api.siliconflow.cn/v1"
        )

    elif provider == "custom":
        return OpenAI(
            api_key=os.getenv("LLM_API_KEY") or "custom",
            base_url=_required_env("LLM_BASE_URL", provider)
        )
        
    else:
        raise ValueError(f"Unsupported API provider: {provider}")

class LeetCodeAgent:
    """LLM-powered agent for answering LeetCode problems and follow-up questions."""

    def __init__(self, client: OpenAI, model: str = "gpt-4o", max_retries: int = 3, language: str = "zh"):
        self.client = client
        self.model = model
        self.max_retries = max_retries

        env_language = os.getenv("APP_LANGUAGE", "zh").lower()
        self.language = (language or env_language).lower()
        print(f"[Debug] LLMAgent Loaded LANGUAGE from env: {self.language}")

        if self.language == "zh":
            self.system_prompt = """你是一个专门为 LeetCode 刷题提供结构化解析的 AI 助手。
            - 必须严格遵循预设的结构化格式输出。
            - 当用户提出追问时，回答应简明扼要。
            - 如果用户给出了新的题号和题目，生成全新的结构化解析。
            - 如果对用户的提问不确定，主动要求澄清。
            """
        elif self.language == "en":
            self.system_prompt = """You are an AI assistant that provides structured explanations for LeetCode problems.
            - Always follow the structured format for problem responses.
            - When users ask follow-up questions, answer concisely and directly.
            - If a new problem number and title are given, generate a new structured response.
            - If unsure, ask the user for clarification.
            """
        self.chat_history = []  # Store conversation context
        self.current_problem = None  # Store the last problem's number & title

        self.problem_dict = self._load_problem_dict()

    def _load_problem_dict(self) -> dict:
        """
        初始化时将 JSON 题库加载到内存中，实现 O(1) 查询。
        """
        # 路径指向上一步创建的 backend/data/leetcode_problems.json
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(project_root,"data","leetcode_problems.json")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print("[Warning] no leetcode_problems.json")
            return {}

    def extract_problem_details(self, user_input: str) -> Optional[Dict[str, str]]:
        """
        优先从输入中正则匹配完整标题。如果只输入了题号，则通过本地字典补全。
        """
        # 1. 尝试提取题号，兼容 "leetcode20题"、"第20题"、"LC20"、"20" 等输入。
        problem_number = None
        patterns = [
            r"(?:leetcode|leet\s*code|lc|problem)\s*#?\s*(\d{1,4})(?:\s*题)?",
            r"(?:第|题目)\s*(\d{1,4})\s*题?",
            r"(?<!\d)(\d{1,4})\s*题",
            r"^\s*(\d{1,4})\s*$",
        ]

        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                problem_number = str(int(match.group(1)))
                break

        if not problem_number:
            return None

        # 2. 尝试从输入中直接提取完整的标题 (应对本地字典中还未收录的新题)
        title_match = re.search(r"(?:Leetcode|LC)?\s*\d{1,4}[:\-\s]+([a-zA-Z\s]+)", user_input, re.IGNORECASE)
        if title_match:
            return {"problem_number": problem_number, "problem_title": title_match.group(1).strip()}

        # 3. 如果用户只输入了题号，直接去 O(1) 字典里拿标题
        problem_title = self.problem_dict.get(problem_number)
        if problem_title:
            return {"problem_number": problem_number, "problem_title": problem_title}

        # 4. 字典里没有，用户也没写标题，直接拦截
        return None
     
    def stream_solution(self, user_input: str):
        """
        流式生成解决方案。利用 yield 关键字，大模型吐出一个 token，就立马推给外层。
        """
        import time 

        # 1. 提取题目信息 (沿用你原本的逻辑)
        problem_details = self.extract_problem_details(user_input)

        if not problem_details:
            print("❓ Could not detect problem number and title. Trying AI-based inference...")
            problem_details = self.infer_problem_details(user_input)

        if not problem_details:
            error_message = "无法识别具体的 LeetCode 题号，请补充说明。" if self.language == "zh" else "I couldn't determine the exact LeetCode problem you're referring to. Can you clarify?"
            # 注意：流式输出中直接 yield 错误信息，让前端打字机打出错误提示，而不是抛出阻塞进程的 ValueError
            yield f"[Error] {error_message}"
            return
            
        self.current_problem = problem_details

        problem_number = problem_details["problem_number"]
        problem_title = problem_details["problem_title"]
        current_date = time.strftime('%Y-%m-%d')

        # 2. 组装 Prompt (这里直接嵌入你原有的 user_prompt 分支逻辑)
        if self.language == "zh":
            user_prompt = f"""
            题目名称: "Leetcode {problem_number}. {problem_title}"

            指令:
            - 提供该题目的考察模式(Pattern)和解题思路。
            - 解释所使用的算法，包含时间复杂度和空间复杂度。
            - 列举该模式的适用场景以及如何扩展到类似题目。
            - 严格按照以下 Markdown 格式输出：

            ---

            ### **LeetCode {problem_number}: {problem_title}** 
             
            | 题号 | 名称 | 上次复习 | 标签 | 题目模式与解答思路 | 适用场景与扩展 |
            |----|------|------------|-----|--------------------------|--------------------|
            | {problem_number} | {problem_title} | {current_date} | {{标签}} | **考察模式:** {{描述题目考察的核心模式和通用解题策略}} <br> **解题思路:** {{解释解法背后的核心思想，以及如何对暴力解法进行优化}} | 1. {{适用该模式的场景 1}} <br> 2. {{适用该模式的场景 2}} <br> 3. {{适用该模式的场景 3}} |

            ---

            ## **🔹 核心算法**
            - **{{算法名称}} (`{{时间复杂度}}`)**
              1. {{步骤 1 解释}}
              2. {{步骤 2 解释}}
              3. {{步骤 3 解释}}
            - **时间复杂度:** `{{O(复杂度)}}`, 原因解释。  
            - **空间复杂度:** `{{O(复杂度)}}`, 原因解释。  

            ---

            ## **🔹 Python 代码实现**
            ```python
            {{最优 Python 解法代码}}
            ```
            """
        else:
            user_prompt = f"""
            Problem Name: "Leetcode {problem_number}. {problem_title}"

            Instructions:
            - Provide the problem pattern and solution approach.
            - Explain the algorithm used, including time and space complexity.
            - List when to use this pattern and how it scales to similar problems.
            - Format the output exactly as follows:

            ---

            ### **LeetCode {problem_number}: {problem_title}** 
             
            | No. | Name | Last Viewed | Tag | Problem Pattern/Solution | When to Use/Scale |
            |----|------|------------|-----|--------------------------|--------------------|
            | {problem_number} | {problem_title} | {current_date} | {{problem_tags}} | **Problem Pattern:** {{Describe the problem pattern and general solution strategy.}} <br> **Solution Approach:** {{Explain the key idea behind the solution, including how it optimizes the problem.}} | 1. {{When to use this pattern, bullet point 1}} <br> 2. {{When to use this pattern, bullet point 2}} <br> 3. {{When to use this pattern, bullet point 3}} |

            ---

            ## **🔹 Algorithm Used**
            - **{{Algorithm Name}} (`{{Time Complexity}}`)**
              1. {{Step 1 explanation}}
              2. {{Step 2 explanation}}
              3. {{Step 3 explanation}}
            - **Time Complexity:** `{{O(complexity)}}`, explanation.  
            - **Space Complexity:** `{{O(complexity)}}`, explanation.  

            ---

            ## **🔹 Python Code**
            ```python
            {{Optimized Python code solution}}
            ```
            """

                # 3. 组装发送给大模型的消息体
        messages = [
            {"role": "system", "content": "You are a professional LeetCode algorithm expert."},
            {"role": "user", "content": user_prompt}
        ]

        full_response = ""
        
        try:
            # 4. 发起流式请求 (这里的 self.client 是你之前 create_llm_client 创建的 OpenAI 实例)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,     # <--- 核心开关
                temperature=0.2  # 降低温度，确保生成的 Markdown 表格格式绝对严谨
            )

            # 5. 循环榨取数据流
            for chunk in response:
                # 兼容不同大模型 API 的返回结构（有些是 chunk.choices，有些直接在顶层）
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    text_chunk = chunk.choices[0].delta.content
                    full_response += text_chunk
                    
                    # 立刻把拿到的字推给 FastAPI 路由，再由 FastAPI 推给前端
                    yield text_chunk

            # (可选) 6. 如果你之前有把历史记录存进 self.messages 的逻辑，可以在这里把完整对话追加进去
            # self.history.append({"role": "user", "content": user_prompt})
            # self.history.append({"role": "assistant", "content": full_response})

        except Exception as e:
            # 如果请求断了或者 API 挂了，优雅地把报错信息通过流推到前端屏幕上
            yield f"\n\n**[LLM Generation Error]**: API 请求异常 ({str(e)})"

    def handle_followup(self, user_query: str) -> str:
        """
        Handles user follow-up questions while maintaining problem context.

        Args:
            user_query (str): The user's follow-up question.

        Returns:
            str: LLM-generated response.
        """
        if not self.current_problem:
            return "I don't have an active problem context. Please specify the problem number or title."

        user_prompt = f"""
        Follow-up question about LeetCode {self.current_problem['problem_number']}: {self.current_problem['problem_title']}.

        Question: "{user_query}"

        Provide a relevant response based on the previous discussion.
        """

        return self._send_message(user_prompt, is_new_question=False)

    def _send_message(self, user_input: str, is_new_question: bool) -> str:
        """
        Sends a message to the OpenAI API while maintaining conversation history.

        Args:
            user_input (str): The user's question or follow-up.
            is_new_question (bool): Whether this is a new question.

        Returns:
            str: OpenAI response.
        """
        retries = 0
        if is_new_question:
            self.chat_history = []  # Reset chat history for a new question

        # Maintain conversation context
        self.chat_history.append({"role": "user", "content": user_input})

        while retries < self.max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": self.system_prompt}] + self.chat_history,
                    temperature=0.7,
                    max_tokens=1500
                )

                answer = response.choices[0].message.content
                self.chat_history.append({"role": "assistant", "content": answer})
                return answer

            except OpenAIError as e:
                print(f"API Error: {e}. Retrying ({retries + 1}/{self.max_retries})...")
                time.sleep(2 ** retries)
                retries += 1

        return "Error: Failed to get a response after retries."
    
# Example Usage
if __name__ == "__main__":
    agent = LeetCodeAgent(model="gpt-4")

    while True:
        user_input = input("\nAsk a question about a LeetCode problem (or type 'exit' to quit): ")
        if user_input.lower() == "exit":
            break
        response = agent.generate_solution(user_input)
        print("\nResponse:\n", response)

        while True:
            followup = input("\nAsk a follow-up (or type 'new' for another problem, 'exit' to quit): ")
            if followup.lower() == "new":
                break
            elif followup.lower() == "exit":
                exit()
            followup_response = agent.handle_followup(followup)
            print("\nAssistant:", followup_response)
