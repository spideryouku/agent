import sys
from api import HelloAgentsLLM
from tools import ToolExecutor, search, calculator
from ReActAgent import ReActAgent

if __name__ == "__main__":
    # 1. 初始化 LLM
    llm = HelloAgentsLLM()

    # 2. 初始化工具执行器并注册工具
    executor = ToolExecutor()
    search_desc = "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。"
    executor.registerTool("Search", search_desc, search)
    
    calc_desc = "一个数学计算器。用于执行复杂的数学运算，如加减乘除。输入必须是合法的数学表达式，例如 '(123 + 456) * 789 / 12'。"
    executor.registerTool("Calculator", calc_desc, calculator)

    # 3. 初始化 ReAct 智能体
    agent = ReActAgent(llm_client=llm, tool_executor=executor)

    # 4. 获取问题 (优先从命令行参数获取，否则使用默认问题)
    if len(sys.argv) > 1:
        question = sys.argv[1]
    else:
        # 默认问题
        question = "抖音平台下内容封面质量标准如何制定"

    print(f"❓ 问题: {question}")
    agent.run(question)
