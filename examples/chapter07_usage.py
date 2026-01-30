# 第七章的Agent使用方式
from dotenv import load_dotenv
load_dotenv()

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 假设 SimpleAgent 与 HelloAgentsLLM 定义在当前目录或其子目录下
# 如果模块名或路径不同，请按实际情况调整
from hello_agents import SimpleAgent, HelloAgentsLLM


agent = SimpleAgent(name="学习助手", llm=HelloAgentsLLM())

# 第一次对话
print("--- 第一次对话 ---")
response1 = agent.run("我叫张三，正在学习Python，目前掌握了基础语法")
print(response1)  # "很好！Python基础语法是编程的重要基础..."

# 第二次对话（新的会话）
print("\n--- 第二次对话 ---")
response2 = agent.run("你还记得我的学习进度吗？")
print(response2)  # "抱歉，我不知道您的学习进度..."
