import sys
from api import HelloAgentsLLM
from PlanAndSolveAgent import PlanAndSolveAgent

if __name__ == "__main__":
    # 1. 初始化 LLM
    llm = HelloAgentsLLM()

    # 2. 初始化 Plan-and-Solve 智能体
    agent = PlanAndSolveAgent(llm_client=llm)

    # 3. 获取问题 (优先从命令行参数获取，否则使用默认问题)
    if len(sys.argv) > 1:
        question = sys.argv[1]
    else:
        # 默认问题
        question = "一个水果店周一卖出了15个苹果。周二卖出的苹果数量是周一的两倍。周三卖出的数量比周二少了5个。请问这三天总共卖出了多少个苹果？"
    
    # 4. 运行智能体
    agent.run(question)
