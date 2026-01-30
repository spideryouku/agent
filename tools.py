import os
from serpapi import SerpApiClient
from dotenv import load_dotenv

load_dotenv()

def search(query: str) -> str:
    """
    一个基于SerpApi的实战网页搜索引擎工具。
    它会智能地解析搜索结果，优先返回直接答案或知识图谱信息。
    """
    print(f"🔍 正在执行 [SerpApi] 网页搜索: {query}")
    try:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            return "错误:SERPAPI_API_KEY 未在 .env 文件中配置。"

        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "gl": "cn",  # 国家代码
            "hl": "zh-cn", # 语言代码
        }
        
        client = SerpApiClient(params)
        results = client.get_dict()
        
        # 智能解析:优先寻找最直接的答案
        if "answer_box_list" in results:
            return "\n".join(results["answer_box_list"])
        if "answer_box" in results and "answer" in results["answer_box"]:
            return results["answer_box"]["answer"]
        if "knowledge_graph" in results and "description" in results["knowledge_graph"]:
            return results["knowledge_graph"]["description"]
        if "organic_results" in results and results["organic_results"]:
            # 如果没有直接答案，则返回前三个有机结果的摘要
            snippets = [
                f"[{i+1}] {res.get('title', '')}\n{res.get('snippet', '')}"
                for i, res in enumerate(results["organic_results"][:3])
            ]
            return "\n\n".join(snippets)
        
        return f"对不起，没有找到关于 '{query}' 的信息。"

    except Exception as e:
        return f"搜索时发生错误: {e}"

def calculator(expression: str) -> str:
    """
    一个强大的数学计算器。
    支持加减乘除、括号等复杂数学运算。
    输入应该是一个合法的数学表达式字符串，例如 "(123 + 456) * 789 / 12"。
    """
    print(f"🧮 正在执行 [Calculator] 计算: {expression}")
    try:
        # 安全检查：仅允许数字和基本运算符
        allowed_chars = set("0123456789+-*/(). %")
        if not all(c in allowed_chars for c in expression if not c.isspace()):
             return "错误: 表达式包含非法字符。仅支持数字和 basic operators (+-*/().%)。"
        
        # 使用 eval 计算，但限制全局和局部命名空间以防注入
        result = eval(expression, {"__builtins__": None}, {})
        return str(result)
    except ZeroDivisionError:
        return "错误: 除数不能为零。"
    except SyntaxError:
        return "错误: 表达式语法无效，请检查括号和运算符。"
    except Exception as e:
        return f"计算错误: {str(e)}"

# --- 工具执行器 ---

class ToolExecutor:
    """
    工具执行器，负责管理和调用所有可用工具。
    """
    def __init__(self):
        # 存储工具的字典，Key为工具名称，Value为(描述, 函数)的元组
        self.tools = {}

    def registerTool(self, name: str, description: str, func):
        """
        注册一个新工具。
        :param name: 工具名称 (如 "Search")
        :param description: 工具的自然语言描述
        :param func: 工具的具体执行函数
        """
        self.tools[name] = (description, func)
        print(f"工具 '{name}' 已注册。")

    def getAvailableTools(self) -> str:
        """
        返回所有可用工具的格式化描述，供LLM在Prompt中使用。
        """
        tools_desc = []
        for name, (desc, _) in self.tools.items():
            tools_desc.append(f"- {name}: {desc}")
        return "\n".join(tools_desc)

    def getTool(self, name: str):
        """
        根据名称获取工具函数。
        """
        if name in self.tools:
            return self.tools[name][1]
        return None

